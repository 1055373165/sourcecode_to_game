"""
Import all models for Alembic auto-generation
"""
from app.database import Base
from app.models.user import User
from app.models.project import Project
from app.models.level import Level, Challenge
from app.models.progress import UserProgress
from app.models.achievement import Achievement, UserAchievement

__all__ = [
    "Base",
    "User",
    "Project",
    "Level",
    "Challenge",
    "UserProgress",
    "Achievement",
    "UserAchievement",
]
