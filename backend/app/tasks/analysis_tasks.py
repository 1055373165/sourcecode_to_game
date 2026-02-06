"""
Background Analysis Tasks

Async tasks for project analysis that run in the background.
Uses FastAPI BackgroundTasks for MVP, can migrate to Celery later.
"""

import logging
import asyncio
import sys
from pathlib import Path
from typing import Optional, Callable
from sqlalchemy.orm import Session

from app.database import SessionLocal

# Add project root to sys.path BEFORE importing AnalysisPipeline
# This ensures the root app package (analyzers, generators) can be found
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.analysis_pipeline import AnalysisPipeline

logger = logging.getLogger(__name__)


# Store for tracking task progress
_task_progress: dict[str, dict] = {}


def get_task_progress(project_id: str) -> Optional[dict]:
    """Get progress for a running analysis task"""
    return _task_progress.get(project_id)


def _progress_callback(project_id: str):
    """Create a progress callback for a specific project"""
    def callback(percent: int, message: str):
        _task_progress[project_id] = {
            "percent": percent,
            "message": message
        }
    return callback


async def analyze_project_task(project_id: str) -> bool:
    """
    Background task to analyze a project
    
    This function is designed to be called from FastAPI's BackgroundTasks.
    It creates its own database session and handles all cleanup.
    
    Args:
        project_id: UUID of the project to analyze
        
    Returns:
        True if analysis succeeded, False otherwise
    """
    logger.info(f"Starting background analysis for project {project_id}")
    
    # Initialize progress tracking
    _task_progress[project_id] = {"percent": 0, "message": "Queued for analysis"}
    
    db: Session = SessionLocal()
    try:
        pipeline = AnalysisPipeline(db)
        callback = _progress_callback(project_id)
        
        success = await pipeline.analyze_project(project_id, callback)
        
        if success:
            logger.info(f"Background analysis completed for project {project_id}")
        else:
            logger.error(f"Background analysis failed for project {project_id}")
        
        return success
        
    except Exception as e:
        logger.exception(f"Unexpected error in background analysis for {project_id}")
        _task_progress[project_id] = {
            "percent": -1,
            "message": f"Error: {str(e)}"
        }
        return False
        
    finally:
        db.close()
        # Keep progress for a while for status checks, then cleanup
        # In production, use Redis or similar for persistence


def run_analysis_sync(project_id: str) -> bool:
    """
    Synchronous wrapper for analysis task
    
    Useful for testing or when async context is not available.
    """
    return asyncio.run(analyze_project_task(project_id))
