"""
Level and Challenge database models
"""
import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Level(Base):
    """Learning level model"""
    __tablename__ = "levels"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    
    # Level info
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(Integer, nullable=False, default=1)  # 1-5
    
    # Code analysis data
    entry_function = Column(String(200), nullable=True)
    call_chain = Column(JSON, nullable=True)  # List of function IDs
    code_snippet = Column(Text, nullable=True)
    
    # Game mechanics
    xp_reward = Column(Integer, nullable=False, default=100)
    estimated_time = Column(Integer, nullable=False, default=10)  # minutes
    
    # Relationships
    project = relationship("Project", back_populates="levels")
    challenges = relationship("Challenge", back_populates="level", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="level", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Level {self.name}>"


class Challenge(Base):
    """Challenge/question within a level"""
    __tablename__ = "challenges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    level_id = Column(String(36), ForeignKey("levels.id"), nullable=False)
    
    # Challenge details
    type = Column(String(50), nullable=False)  # multiple_choice, code_tracing, etc.
    question = Column(JSON, nullable=False)  # {"prompt": "...", "options": [...]}
    answer = Column(JSON, nullable=False)  # Correct answer (will be hidden from API)
    hints = Column(JSON, nullable=True)  # List of hints
    points = Column(Integer, nullable=False, default=10)
    
    # Relationships
    level = relationship("Level", back_populates="challenges")
    
    def __repr__(self):
        return f"<Challenge {self.type} in {self.level_id}>"
