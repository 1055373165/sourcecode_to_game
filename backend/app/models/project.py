"""
Project database model
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class AnalysisStatus(str, enum.Enum):
    """Project analysis status"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class Project(Base):
    """Project model representing a codebase to analyze"""
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    language = Column(String(20), nullable=False)  # python, golang
    github_url = Column(String(255), nullable=True)
    difficulty = Column(Integer, nullable=False, default=1)  # 1-5
    total_levels = Column(Integer, default=0, nullable=False)
    
    # Analysis tracking
    analysis_status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False)
    analyzed_at = Column(DateTime, nullable=True)
    analysis_error = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    levels = relationship("Level", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project {self.name} ({self.language})>"
