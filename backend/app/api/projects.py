"""
Project API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Query, status
from sqlalchemy.orm import Session


from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project, AnalysisStatus
from app.models.level import Level
from app.models.progress import UserProgress
from app.schemas.project import ProjectResponse, LevelResponse
from app.schemas.common import PaginatedResponse
from app.core.exceptions import ProjectNotFoundException

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    language: Optional[str] = Query(None, description="Filter by language (python, golang)"),
    difficulty: Optional[int] = Query(None, ge=1, le=5, description="Filter by difficulty (1-5)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all projects with optional filters
    
    - **language**: Filter by programming language (python, golang)
    - **difficulty**: Filter by difficulty level (1-5)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    
    Returns paginated list of projects
    """
    # Build query
    query = db.query(Project).filter(Project.analysis_status == AnalysisStatus.COMPLETED)
    
    # Apply filters
    if language:
        query = query.filter(Project.language == language.lower())
    if difficulty:
        query = query.filter(Project.difficulty == difficulty)
    
    # Get total count
    total = query.count()
    
    # Pagination
    offset = (page - 1) * page_size
    projects = query.offset(offset).limit(page_size).all()
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=[ProjectResponse.model_validate(p) for p in projects],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed project information
    
    - **project_id**: UUID of the project
    
    Returns project details with all levels
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise ProjectNotFoundException()
    
    return ProjectResponse.model_validate(project)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    background_tasks: BackgroundTasks,
    github_url: str = Query(..., description="GitHub repository URL"),
    name: str = Query(..., description="Project display name"),
    language: str = Query(None, description="Programming language (auto-detected if not provided)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    """
    Create a new project from GitHub URL and start analysis
    
    This endpoint creates a project record and triggers background analysis.
    The analysis will clone the repository, parse the code, and generate
    learning levels automatically.
    
    - **github_url**: GitHub repository URL (e.g., https://github.com/owner/repo)
    - **name**: Display name for the project
    - **language**: Programming language (python, golang). Auto-detected if not provided.
    
    Returns created project with PENDING status. Poll /projects/{id}/progress for updates.
    """
    from fastapi import HTTPException
    from app.services.github_service import github_service, InvalidURLError
    from app.tasks.analysis_tasks import analyze_project_task
    
    # Validate GitHub URL
    if not github_service.validate_url(github_url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GitHub URL. Expected format: https://github.com/owner/repo"
        )
    
    # Check if project already exists
    existing = db.query(Project).filter(Project.github_url == github_url).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Project with this GitHub URL already exists (id: {existing.id})"
        )
    
    # Create project record
    new_project = Project(
        name=name,
        github_url=github_url,
        language=language.lower() if language else None,
        analysis_status=AnalysisStatus.PENDING
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # Trigger background analysis
    background_tasks.add_task(analyze_project_task, str(new_project.id))

    
    return ProjectResponse.model_validate(new_project)


@router.get("/{project_id}/progress")
async def get_analysis_progress(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analysis progress for a project
    
    Returns current analysis status and progress percentage.
    Poll this endpoint to track background analysis.
    """
    from app.tasks.analysis_tasks import get_task_progress
    
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ProjectNotFoundException()
    
    # Get live progress if available
    progress = get_task_progress(project_id)
    
    return {
        "project_id": project_id,
        "status": project.analysis_status.value if hasattr(project.analysis_status, 'value') else project.analysis_status,
        "progress": progress.get("percent", 0) if progress else (100 if project.analysis_status == AnalysisStatus.COMPLETED else 0),
        "message": progress.get("message", "") if progress else "",
        "total_levels": project.total_levels
    }


@router.get("/{project_id}/levels")
async def get_project_levels(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all levels for a project
    
    Returns list of levels with their challenges.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ProjectNotFoundException()
    
    levels = db.query(Level).filter(Level.project_id == project_id).order_by(Level.id).all()
    
    result = []
    for level in levels:
        # Get user's progress on this level
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.level_id == level.id
        ).first()
        
        result.append({
            "id": level.id,
            "name": level.name,
            "description": level.description,
            "difficulty": level.difficulty,
            "entry_function": level.entry_function,
            "code_snippet": level.code_snippet,
            "xp_reward": level.xp_reward,
            "estimated_time": level.estimated_time,
            "challenges_count": len(level.challenges),
            "is_completed": progress.completed if progress else False,
            "score": progress.score if progress else 0,
        })
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "total_levels": len(result),
        "levels": result
    }
