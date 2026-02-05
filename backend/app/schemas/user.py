"""
Pydantic schemas for user data
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class UserProgressResponse(BaseModel):
    """Schema for user progress on a level"""
    level_id: str
    level_name: str
    status: str
    attempts: int
    best_score: int
    max_score: int
    time_spent: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ProjectProgressResponse(BaseModel):
    """Schema for user progress on a project"""
    project_id: str
    project_name: str
    total_levels: int
    completed_levels: int
    completion_percentage: float
    average_score: int


class AchievementResponse(BaseModel):
    """Schema for achievement"""
    id: str
    name: str
    description: str
    icon: str
    category: str
    xp_reward: int
    unlocked: bool
    unlocked_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """Schema for user statistics"""
    total_xp: int
    current_level: int
    xp_to_next_level: int
    levels_completed: int
    projects_completed: int
    perfect_scores: int
    current_streak: int
    longest_streak: int
    total_time_spent: int  # seconds
