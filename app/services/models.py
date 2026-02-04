"""
Service Data Models

Shared data models used across all game engine services.
These complement the core analyzer models with user-specific data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class LevelStatus(Enum):
    """Status of a user's progress on a level"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class AchievementCategory(Enum):
    """Categories for achievements"""
    PROGRESSION = "progression"
    PERFORMANCE = "performance"
    SPECIAL = "special"
    SOCIAL = "social"


@dataclass
class LevelProgress:
    """Tracks user progress on a single level"""
    user_id: str
    project_id: str
    level_id: str
    status: LevelStatus
    attempts: int = 0
    best_score: int = 0
    max_score: int = 100
    time_spent: int = 0  # seconds
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    hints_used: int = 0
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.max_score == 0:
            return 0.0
        return (self.best_score / self.max_score) * 100
    
    @property
    def is_perfect(self) -> bool:
        """Check if user got perfect score"""
        return self.best_score == self.max_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "user_id": self.user_id,
            "project_id": self.project_id,
            "level_id": self.level_id,
            "status": self.status.value,
            "attempts": self.attempts,
            "best_score": self.best_score,
            "max_score": self.max_score,
            "completion_percentage": self.completion_percentage,
            "is_perfect": self.is_perfect,
            "time_spent": self.time_spent,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "hints_used": self.hints_used
        }


@dataclass
class ProjectProgress:
    """Tracks user progress on an entire project"""
    user_id: str
    project_id: str
    project_name: str
    total_levels: int
    completed_levels: int = 0
    current_level_id: Optional[str] = None
    total_xp_earned: int = 0
    total_time_spent: int = 0  # seconds
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    level_progress: List[LevelProgress] = field(default_factory=list)
    
    @property
    def completion_percentage(self) -> float:
        """Calculate overall project completion"""
        if self.total_levels == 0:
            return 0.0
        return (self.completed_levels / self.total_levels) * 100
    
    @property
    def is_completed(self) -> bool:
        """Check if project is fully completed"""
        return self.completed_levels == self.total_levels
    
    @property
    def average_score(self) -> float:
        """Calculate average score across all levels"""
        if not self.level_progress:
            return 0.0
        completed = [lp for lp in self.level_progress if lp.status == LevelStatus.COMPLETED]
        if not completed:
            return 0.0
        total_score = sum(lp.best_score for lp in completed)
        total_max = sum(lp.max_score for lp in completed)
        return (total_score / total_max * 100) if total_max > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "user_id": self.user_id,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "total_levels": self.total_levels,
            "completed_levels": self.completed_levels,
            "completion_percentage": self.completion_percentage,
            "is_completed": self.is_completed,
            "current_level_id": self.current_level_id,
            "total_xp_earned": self.total_xp_earned,
            "total_time_spent": self.total_time_spent,
            "average_score": self.average_score,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "levels": [lp.to_dict() for lp in self.level_progress]
        }


@dataclass
class ChallengeResult:
    """Result of evaluating a single challenge"""
    challenge_id: str
    is_correct: bool
    points_earned: int
    max_points: int
    feedback: str
    hints: List[str] = field(default_factory=list)
    execution_time: Optional[float] = None  # For code challenges
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "challenge_id": self.challenge_id,
            "is_correct": self.is_correct,
            "points_earned": self.points_earned,
            "max_points": self.max_points,
            "feedback": self.feedback,
            "hints": self.hints,
            "execution_time": self.execution_time
        }


@dataclass
class LevelResult:
    """Result of completing a level"""
    level_id: str
    level_completed: bool
    score: int
    max_score: int
    challenge_results: List[ChallengeResult]
    time_taken: int  # seconds
    hints_used: int
    is_first_attempt: bool
    is_perfect_score: bool
    
    @property
    def percentage_score(self) -> float:
        """Get percentage score"""
        if self.max_score == 0:
            return 0.0
        return (self.score / self.max_score) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "level_id": self.level_id,
            "level_completed": self.level_completed,
            "score": self.score,
            "max_score": self.max_score,
            "percentage_score": self.percentage_score,
            "is_perfect_score": self.is_perfect_score,
            "is_first_attempt": self.is_first_attempt,
            "time_taken": self.time_taken,
            "hints_used": self.hints_used,
            "challenge_results": [cr.to_dict() for cr in self.challenge_results]
        }


@dataclass
class XPAward:
    """Details of an XP award"""
    amount: int
    reason: str
    breakdown: Dict[str, int]  # {"base": 100, "perfect_bonus": 50, ...}
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "amount": self.amount,
            "reason": self.reason,
            "breakdown": self.breakdown,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class LevelUp:
    """Details of a level up event"""
    old_level: int
    new_level: int
    xp_to_next: int
    rewards: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "old_level": self.old_level,
            "new_level": self.new_level,
            "xp_to_next": self.xp_to_next,
            "rewards": self.rewards
        }


@dataclass
class UserStats:
    """Overall user statistics"""
    user_id: str
    total_xp: int = 0
    current_level: int = 1
    xp_to_next_level: int = 100
    levels_completed: int = 0
    projects_completed: int = 0
    perfect_scores: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    total_time_spent: int = 0  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "total_xp": self.total_xp,
            "current_level": self.current_level,
            "xp_to_next_level": self.xp_to_next_level,
            "levels_completed": self.levels_completed,
            "projects_completed": self.projects_completed,
            "perfect_scores": self.perfect_scores,
            "current_streak": self.current_streak,
            "longest_streak": self.longest_streak,
            "last_activity_date": self.last_activity_date.isoformat() if self.last_activity_date else None,
            "total_time_spent": self.total_time_spent
        }


@dataclass
class Achievement:
    """An achievement that users can unlock"""
    id: str
    name: str
    description: str
    icon: str
    category: AchievementCategory
    xp_reward: int
    condition: Dict[str, Any]  # e.g., {"type": "levels_completed", "count": 5}
    unlocked_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category.value,
            "xp_reward": self.xp_reward,
            "condition": self.condition,
            "unlocked_at": self.unlocked_at.isoformat() if self.unlocked_at else None
        }


@dataclass
class LeaderboardEntry:
    """Entry in a leaderboard"""
    rank: int
    user_id: str
    username: str
    score: int
    avatar: Optional[str] = None
    level: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rank": self.rank,
            "user_id": self.user_id,
            "username": self.username,
            "score": self.score,
            "avatar": self.avatar,
            "level": self.level
        }
