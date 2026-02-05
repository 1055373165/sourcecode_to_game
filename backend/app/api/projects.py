"""
Project API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
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
    github_url: str = Query(..., description="GitHub repository URL"),
    name: str = Query(..., description="Project display name"),
    language: str = Query(..., description="Programming language"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project from GitHub URL (Admin only for MVP)
    
    This endpoint creates a project record and triggers background analysis.
    For MVP, the analysis is not implemented yet - projects must be manually analyzed.
    
    - **github_url**: GitHub repository URL
    - **name**: Display name for the project
    - **language**: Programming language (python, golang)
    
    Returns created project with PENDING status
    """
    # For MVP, only admins can create projects
    if not current_user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create projects"
        )
    
    # Create project record
    new_project = Project(
        name=name,
        github_url=github_url,
        language=language.lower(),
        analysis_status=AnalysisStatus.PENDING
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    # TODO: Trigger background analysis job
    # For MVP, projects will be analyzed manually
    
    return ProjectResponse.model_validate(new_project)
