"""
Achievement models
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class Achievement(Base):
    """Achievement definition (template)"""
    __tablename__ = "achievements"
    
    id = Column(String(50), primary_key=True)  # e.g., "first_level"
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), nullable=False)  # emoji or icon name
    category = Column(String(50), nullable=False)  # progression, performance, special
    xp_reward = Column(Integer, nullable=False, default=0)
    
    # Condition for unlocking (flexible JSON structure)
    condition = Column(JSON, nullable=False)  # {"type": "levels_completed", "count": 5}
    
    # Relationships
    user_unlocks = relationship("UserAchievement", back_populates="achievement")
    
    def __repr__(self):
        return f"<Achievement {self.name}>"


class UserAchievement(Base):
    """Tracks which achievements a user has unlocked"""
    __tablename__ = "user_achievements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    achievement_id = Column(String(50), ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_unlocks")
    
    def __repr__(self):
        return f"<UserAchievement {self.achievement_id} for {self.user_id}>"
