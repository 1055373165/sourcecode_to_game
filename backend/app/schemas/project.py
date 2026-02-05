"""
Pydantic schemas for projects and levels
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str
    description: Optional[str] = None
    language: str  # python, golang
    github_url: Optional[str] = None
    difficulty: int = 1


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    id: str
    total_levels: int
    analysis_status: str
    analyzed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LevelBase(BaseModel):
    """Base level schema"""
    name: str
    description: Optional[str] = None
    difficulty: int = 1
    xp_reward: int = 100
    estimated_time: int = 10


class LevelResponse(LevelBase):
    """Schema for level response"""
    id: str
    project_id: str
    entry_function: Optional[str] = None
    call_chain: Optional[List[str]] = None
    code_snippet: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChallengeResponse(BaseModel):
    """Schema for challenge response (without answer)"""
    id: str
    type: str
    question: Dict[str, Any]
    hints: Optional[List[str]] = None
    points: int
    
    class Config:
        from_attributes = True


class LevelDetailResponse(LevelResponse):
    """Schema for level with challenges"""
    challenges: List[ChallengeResponse]


class LevelSubmission(BaseModel):
    """Schema for submitting level answers"""
    answers: Dict[str, Any]  # {challenge_id: user_answer}


class ChallengeResult(BaseModel):
    """Schema for single challenge result"""
    challenge_id: str
    is_correct: bool
    points_earned: int
    max_points: int
    feedback: str


class LevelSubmissionResult(BaseModel):
    """Schema for level submission result"""
    level_completed: bool
    score: int
    max_score: int
    xp_earned: int
    challenge_results: List[ChallengeResult]
    achievements_unlocked: Optional[List[Dict[str, Any]]] = None
