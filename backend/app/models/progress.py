"""
User progress tracking models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ProgressStatus(str, enum.Enum):
    """User progress status for a level"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class UserProgress(Base):
    """Tracks user progress on a specific level"""
    __tablename__ = "user_progress"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    level_id = Column(String(36), ForeignKey("levels.id"), nullable=False, index=True)
    
    # Progress tracking
    status = Column(SQLEnum(ProgressStatus), default=ProgressStatus.NOT_STARTED, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    best_score = Column(Integer, default=0, nullable=False)
    max_score = Column(Integer, default=100, nullable=False)
    time_spent = Column(Integer, default=0, nullable=False)  # seconds
    hints_used = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    level = relationship("Level", back_populates="progress")
    
    def __repr__(self):
        return f"<UserProgress {self.user_id} on {self.level_id}: {self.status.value}>"
