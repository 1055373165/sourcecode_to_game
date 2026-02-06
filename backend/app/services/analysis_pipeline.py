"""
Analysis Pipeline Service

Orchestrates the complete analysis workflow:
1. Clone repository
2. Run language analyzer
3. Generate levels and challenges
4. Save results to database
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.github_service import github_service, RepoInfo, GitHubServiceError
from app.models.project import Project, AnalysisStatus
from app.models.level import Level, Challenge as DBChallenge

logger = logging.getLogger(__name__)

# Project root path for loading analyzer modules
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def _load_module_from_path(name: str, file_path: Path):
    """Load a Python module directly from its file path using importlib"""
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")
    module = importlib.util.module_from_spec(spec)
    # Add to sys.modules to handle internal imports within the module
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _get_analyzer_modules():
    """
    Lazy load analyzer modules from project root app package.
    Uses importlib to load directly from file paths to avoid package conflicts.
    """
    # First, load the core models module (needed by analyzers)
    models_core_path = PROJECT_ROOT / "app" / "models" / "core.py"
    models_core = _load_module_from_path("app.models.core", models_core_path)
    
    # Load analyzers base module
    analyzers_base_path = PROJECT_ROOT / "app" / "analyzers" / "base.py"
    analyzers_base = _load_module_from_path("app.analyzers.base", analyzers_base_path)
    
    # Load Python analyzer - this triggers AnalyzerFactory.register() for Python
    python_analyzer_path = PROJECT_ROOT / "app" / "analyzers" / "python_analyzer.py"
    _load_module_from_path("app.analyzers.python_analyzer", python_analyzer_path)
    
    # Load level generator
    generators_path = PROJECT_ROOT / "app" / "generators" / "level_generator.py"
    level_generator = _load_module_from_path("app.generators.level_generator", generators_path)
    
    return (
        analyzers_base.AnalyzerFactory,
        analyzers_base.AnalysisError,
        level_generator.LevelGenerator,
        models_core.Language
    )










class AnalysisPipelineError(Exception):
    """Base exception for analysis pipeline errors"""
    pass


class UnsupportedLanguageError(AnalysisPipelineError):
    """Raised when project language is not supported"""
    pass


class AnalysisPipeline:
    """
    Orchestrates the complete project analysis workflow
    
    Pipeline stages:
    1. Clone: Download repository from GitHub
    2. Analyze: Parse source code and build call graph
    3. Generate: Create learning levels and challenges
    4. Persist: Save results to database
    """
    
    SUPPORTED_LANGUAGES = {'python', 'golang'}
    
    def __init__(self, db: Session):
        """
        Initialize pipeline with database session
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    async def analyze_project(
        self, 
        project_id: str,
        progress_callback: Optional[callable] = None
    ) -> bool:
        """
        Run complete analysis pipeline for a project
        
        Args:
            project_id: ID of the project to analyze
            progress_callback: Optional callback for progress updates (0-100)
            
        Returns:
            True if analysis succeeded, False otherwise
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            logger.error(f"Project not found: {project_id}")
            return False
        
        repo_info: Optional[RepoInfo] = None
        
        # Load analyzer modules early so AnalysisError is available in except block
        AnalyzerFactory, AnalysisError, LevelGenerator, Language = _get_analyzer_modules()
        
        try:

            # Update status to ANALYZING
            self._update_status(project, AnalysisStatus.ANALYZING)
            self._report_progress(progress_callback, 5, "Starting analysis...")
            
            # Stage 1: Clone repository
            logger.info(f"Stage 1: Cloning repository for project {project.name}")
            self._report_progress(progress_callback, 10, "Cloning repository...")
            
            repo_info = await github_service.clone_repository(project.github_url)
            
            # Validate language
            detected_lang = repo_info.detected_language
            if detected_lang not in self.SUPPORTED_LANGUAGES:
                raise UnsupportedLanguageError(
                    f"Language '{detected_lang}' is not supported. "
                    f"Supported: {', '.join(self.SUPPORTED_LANGUAGES)}"
                )
            
            # Use detected language if not specified
            if not project.language:
                project.language = detected_lang
            
            self._report_progress(progress_callback, 25, f"Repository cloned ({repo_info.file_count} files)")
            
            # Stage 2: Run analyzer
            logger.info(f"Stage 2: Analyzing {detected_lang} source code")
            self._report_progress(progress_callback, 30, "Analyzing source code...")
            
            language_enum = Language.PYTHON if detected_lang == 'python' else Language.GOLANG

            analyzer = AnalyzerFactory.create(language_enum, repo_info.local_path)
            analysis_result = analyzer.analyze()
            
            if not analysis_result or not analysis_result.call_graph:
                raise AnalysisPipelineError("Analysis produced no results")

            
            self._report_progress(
                progress_callback, 50, 
                f"Found {len(analysis_result.call_graph.nodes)} functions"
            )
            
            # Stage 3: Generate levels
            logger.info("Stage 3: Generating learning levels")
            self._report_progress(progress_callback, 55, "Generating learning levels...")
            
            generator = LevelGenerator(analysis_result.call_graph)
            levels = generator.generate_levels(max_levels=10)
            
            if not levels:
                raise AnalysisPipelineError("No levels could be generated")
            
            self._report_progress(progress_callback, 75, f"Generated {len(levels)} levels")
            
            # Stage 4: Persist to database
            logger.info("Stage 4: Saving results to database")
            self._report_progress(progress_callback, 80, "Saving to database...")
            
            self._save_levels(project, levels)
            
            # Update project status
            project.analysis_status = AnalysisStatus.COMPLETED
            project.analyzed_at = datetime.utcnow()
            project.total_levels = len(levels)
            self.db.commit()
            
            self._report_progress(progress_callback, 100, "Analysis complete!")
            logger.info(f"Successfully analyzed project {project.name}: {len(levels)} levels")
            
            return True
            
        except GitHubServiceError as e:
            logger.error(f"GitHub error for project {project_id}: {e}")
            self._update_status(project, AnalysisStatus.FAILED, str(e))
            return False
            
        except AnalysisError as e:
            logger.error(f"Analysis error for project {project_id}: {e}")
            self._update_status(project, AnalysisStatus.FAILED, str(e))
            return False
            
        except Exception as e:
            logger.exception(f"Unexpected error analyzing project {project_id}")
            self._update_status(project, AnalysisStatus.FAILED, str(e))
            return False
            
        finally:
            # Cleanup cloned repository
            if repo_info and repo_info.local_path:
                github_service.cleanup(repo_info.local_path)
    
    def _update_status(
        self, 
        project: Project, 
        status: AnalysisStatus, 
        error_message: Optional[str] = None
    ):
        """Update project analysis status"""
        project.analysis_status = status
        if error_message:
            project.description = f"{project.description or ''}\n\nError: {error_message}"
        self.db.commit()
    
    def _report_progress(
        self, 
        callback: Optional[callable], 
        percent: int, 
        message: str
    ):
        """Report progress if callback provided"""
        if callback:
            callback(percent, message)
        logger.info(f"Progress [{percent}%]: {message}")
    
    def _save_levels(self, project: Project, levels: list):
        """Save generated levels to database"""
        for i, level in enumerate(levels):
            db_level = Level(
                project_id=str(project.id),
                name=level.name,
                description=level.description,
                difficulty=level.difficulty.value if hasattr(level.difficulty, 'value') else level.difficulty,
                entry_function=level.entry_function,
                call_chain=level.call_chain,
                code_snippet=level.code_snippet,
                xp_reward=level.xp_reward,
                estimated_time=getattr(level, 'estimated_time', 10),
            )
            self.db.add(db_level)
            self.db.flush()  # Get the ID

            
            # Save challenges
            for j, challenge in enumerate(level.challenges):
                db_challenge = DBChallenge(
                    level_id=str(db_level.id),
                    type=challenge.type.value if hasattr(challenge.type, 'value') else challenge.type,
                    question=challenge.question,
                    answer=challenge.answer,
                    hints=challenge.hints,
                    points=challenge.points,
                )
                self.db.add(db_challenge)

        
        self.db.commit()
