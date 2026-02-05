"""
User progress and stats API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.level import Level
from app.models.progress import UserProgress, ProgressStatus
from app.models.achievement import Achievement, UserAchievement
from app.schemas.user import (
    UserStatsResponse, 
    UserProgressResponse, 
    ProjectProgressResponse,
    AchievementResponse
)

router = APIRouter()


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's overall statistics
    
    Returns:
    - Total XP and current level
    - Levels completed count
    - Projects completed count  
    - Perfect score count
    - Current streak (mock data for MVP)
    - Total time spent
    """
    # Count progress stats
    levels_completed = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.status == ProgressStatus.COMPLETED
    ).count()
    
    # Count perfect scores (100%)
    perfect_scores = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.best_score >= 100
    ).count()
    
    # Calculate total time spent (sum of all progress)
    total_time = db.query(func.sum(UserProgress.time_spent)).filter(
        UserProgress.user_id == current_user.id
    ).scalar() or 0
    
    # Count unique projects with completed levels
    projects_completed = db.query(func.count(func.distinct(Level.project_id))).join(
        UserProgress, UserProgress.level_id == Level.id
    ).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.status == ProgressStatus.COMPLETED
    ).scalar() or 0
    
    # Calculate XP to next level (1000 XP per level)
    current_level = current_user.current_level
    xp_for_next = ((current_level) * 1000) - current_user.total_xp
    
    return UserStatsResponse(
        total_xp=current_user.total_xp,
        current_level=current_user.current_level,
        xp_to_next_level=max(0, xp_for_next),
        levels_completed=levels_completed,
        projects_completed=projects_completed,
        perfect_scores=perfect_scores,
        current_streak=0,  # TODO: Implement streak tracking
        longest_streak=0,  # TODO: Implement streak tracking
        total_time_spent=total_time
    )


@router.get("/me/progress", response_model=List[ProjectProgressResponse])
async def get_user_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's progress across all projects
    
    Returns list of projects with:
    - Project info
    - Total levels and completed levels
    - Average score
    - Completion percentage
    """
    # Get all projects
    projects = db.query(Project).all()
    
    result = []
    for project in projects:
        # Get all levels for this project
        total_levels = len(project.levels)
        
        if total_levels == 0:
            continue
        
        # Get user's progress on this project's levels
        progress_records = db.query(UserProgress).join(
            Level, UserProgress.level_id == Level.id
        ).filter(
            Level.project_id == project.id,
            UserProgress.user_id == current_user.id
        ).all()
        
        completed = sum(1 for p in progress_records if p.status == ProgressStatus.COMPLETED)
        avg_score = sum(p.best_score for p in progress_records) / len(progress_records) if progress_records else 0
        
        result.append(ProjectProgressResponse(
            project_id=project.id,
            project_name=project.name,
            total_levels=total_levels,
            completed_levels=completed,
            completion_percentage=(completed / total_levels * 100) if total_levels > 0 else 0,
            average_score=int(avg_score)
        ))
    
    return result


@router.get("/me/achievements", response_model=List[AchievementResponse])
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's unlocked achievements
    
    Returns all achievements with unlock status
    """
    # Get all achievements
    all_achievements = db.query(Achievement).all()
    
    # Get user's unlocked achievements
    unlocked = db.query(UserAchievement).filter(
        UserAchievement.user_id == current_user.id
    ).all()
    
    unlocked_ids = {ua.achievement_id for ua in unlocked}
    unlocked_map = {ua.achievement_id: ua.unlocked_at for ua in unlocked}
    
    result = []
    for achievement in all_achievements:
        result.append(AchievementResponse(
            id=achievement.id,
            name=achievement.name,
            description=achievement.description,
            icon=achievement.icon,
            category=achievement.category,
            xp_reward=achievement.xp_reward,
            unlocked=achievement.id in unlocked_ids,
            unlocked_at=unlocked_map.get(achievement.id)
        ))
    
    return result


@router.get("/me/progress/{project_id}", response_model=List[UserProgressResponse])
async def get_project_progress(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed progress for a specific project
    
    Returns progress for each level in the project
    """
    # Get all levels for this project
    levels = db.query(Level).filter(Level.project_id == project_id).all()
    
    result = []
    for level in levels:
        # Get user's progress for this level
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.level_id == level.id
        ).first()
        
        if progress:
            result.append(UserProgressResponse(
                level_id=level.id,
                level_name=level.name,
                status=progress.status.value,
                attempts=progress.attempts,
                best_score=progress.best_score,
                max_score=progress.max_score,
                time_spent=progress.time_spent,
                started_at=progress.started_at,
                completed_at=progress.completed_at
            ))
        else:
            # Level not started yet
            result.append(UserProgressResponse(
                level_id=level.id,
                level_name=level.name,
                status="not_started",
                attempts=0,
                best_score=0,
                max_score=100,
                time_spent=0,
                started_at=None,
                completed_at=None
            ))
    
    return result
