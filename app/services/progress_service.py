"""
Progress Tracking Service

Handles user progress through projects and levels, including:
- Starting and completing levels
- Tracking scores and attempts
- Unlocking next levels
- Calculating completion percentages
"""

from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from app.services.models import (
    LevelProgress, ProjectProgress, LevelResult, LevelStatus
)
from app.models.core import Level


class ProgressService:
    """
    Service for tracking user progress through the learning platform
    
    In a production environment, this would interact with a database.
    For now, it uses in-memory storage for demonstration.
    """
    
    def __init__(self):
        # In-memory storage (would be database in production)
        self._level_progress: Dict[str, LevelProgress] = {}
        self._project_progress: Dict[str, ProjectProgress] = {}
    
    def get_user_progress(self, user_id: str, project_id: str) -> Optional[ProjectProgress]:
        """
        Get user's progress for a specific project
        
        Args:
            user_id: User identifier
            project_id: Project identifier
        
        Returns:
            ProjectProgress if exists, None otherwise
        """
        key = f"{user_id}:{project_id}"
        return self._project_progress.get(key)
    
    def initialize_project(
        self,
        user_id: str,
        project_id: str,
        project_name: str,
        levels: List[Level]
    ) -> ProjectProgress:
        """
        Initialize progress tracking for a new project
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            project_name: Human-readable project name
            levels: List of levels in the project
        
        Returns:
            Initialized ProjectProgress
        """
        key = f"{user_id}:{project_id}"
        
        # Check if already exists
        if key in self._project_progress:
            return self._project_progress[key]
        
        # Create level progress entries
        level_progress_list = []
        for level in levels:
            lp = LevelProgress(
                user_id=user_id,
                project_id=project_id,
                level_id=level.id,
                status=LevelStatus.NOT_STARTED,
                max_score=sum(c.points for c in level.challenges)
            )
            lp_key = f"{user_id}:{project_id}:{level.id}"
            self._level_progress[lp_key] = lp
            level_progress_list.append(lp)
        
        # Create project progress
        project_progress = ProjectProgress(
            user_id=user_id,
            project_id=project_id,
            project_name=project_name,
            total_levels=len(levels),
            current_level_id=levels[0].id if levels else None,
            started_at=datetime.now(),
            level_progress=level_progress_list
        )
        
        self._project_progress[key] = project_progress
        return project_progress
    
    def start_level(self, user_id: str, project_id: str, level_id: str) -> LevelProgress:
        """
        Mark a level as started
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            level_id: Level identifier
        
        Returns:
            Updated LevelProgress
        
        Raises:
            ValueError: If level not found or not unlocked
        """
        lp_key = f"{user_id}:{project_id}:{level_id}"
        
        if lp_key not in self._level_progress:
            raise ValueError(f"Level {level_id} not found for user {user_id}")
        
        level_progress = self._level_progress[lp_key]
        
        # Only update if not started yet
        if level_progress.status == LevelStatus.NOT_STARTED:
            level_progress.status = LevelStatus.IN_PROGRESS
            level_progress.started_at = datetime.now()
        
        return level_progress
    
    def complete_level(
        self,
        user_id: str,
        project_id: str,
        level_id: str,
        level_result: LevelResult
    ) -> LevelProgress:
        """
        Record level completion
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            level_id: Level identifier
            level_result: Results from the level attempt
        
        Returns:
            Updated LevelProgress
        
        Raises:
            ValueError: If level not found
        """
        lp_key = f"{user_id}:{project_id}:{level_id}"
        
        if lp_key not in self._level_progress:
            raise ValueError(f"Level {level_id} not found for user {user_id}")
        
        level_progress = self._level_progress[lp_key]
        
        # Update attempts
        level_progress.attempts += 1
        
        # Update best score if this is better
        if level_result.score > level_progress.best_score:
            level_progress.best_score = level_result.score
        
        # Update time spent
        level_progress.time_spent += level_result.time_taken
        
        # Update hints used
        level_progress.hints_used += level_result.hints_used
        
        # Mark as completed if score threshold met (e.g., 70%)
        completion_threshold = 0.7
        if level_result.percentage_score >= completion_threshold * 100:
            if level_progress.status != LevelStatus.COMPLETED:
                level_progress.status = LevelStatus.COMPLETED
                level_progress.completed_at = datetime.now()
                
                # Update project progress
                self._update_project_progress(user_id, project_id)
        
        return level_progress
    
    def _update_project_progress(self, user_id: str, project_id: str) -> None:
        """
        Update project-level statistics after level completion
        
        Args:
            user_id: User identifier
            project_id: Project identifier
        """
        key = f"{user_id}:{project_id}"
        
        if key not in self._project_progress:
            return
        
        project_progress = self._project_progress[key]
        
        # Count completed levels
        completed_count = sum(
            1 for lp in project_progress.level_progress
            if lp.status == LevelStatus.COMPLETED
        )
        project_progress.completed_levels = completed_count
        
        # Update total time
        total_time = sum(lp.time_spent for lp in project_progress.level_progress)
        project_progress.total_time_spent = total_time
        
        # Check if project is completed
        if completed_count == project_progress.total_levels:
            if not project_progress.completed_at:
                project_progress.completed_at = datetime.now()
    
    def unlock_next_level(self, user_id: str, project_id: str, current_level_id: str) -> Optional[str]:
        """
        Unlock the next level after completing current one
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            current_level_id: ID of the level just completed
        
        Returns:
            ID of the next unlocked level, or None if no more levels
        """
        key = f"{user_id}:{project_id}"
        
        if key not in self._project_progress:
            return None
        
        project_progress = self._project_progress[key]
        
        # Find current level index
        current_index = None
        for i, lp in enumerate(project_progress.level_progress):
            if lp.level_id == current_level_id:
                current_index = i
                break
        
        if current_index is None or current_index >= len(project_progress.level_progress) - 1:
            return None  # No next level
        
        # Get next level
        next_level = project_progress.level_progress[current_index + 1]
        
        # Update current level in project
        project_progress.current_level_id = next_level.level_id
        
        return next_level.level_id
    
    def get_level_progress(
        self,
        user_id: str,
        project_id: str,
        level_id: str
    ) -> Optional[LevelProgress]:
        """
        Get progress for a specific level
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            level_id: Level identifier
        
        Returns:
            LevelProgress if exists, None otherwise
        """
        key = f"{user_id}:{project_id}:{level_id}"
        return self._level_progress.get(key)
    
    def get_completion_percentage(self, user_id: str, project_id: str) -> float:
        """
        Calculate overall completion percentage for a project
        
        Args:
            user_id: User identifier
            project_id: Project identifier
        
        Returns:
            Completion percentage (0-100)
        """
        project_progress = self.get_user_progress(user_id, project_id)
        
        if not project_progress:
            return 0.0
        
        return project_progress.completion_percentage
    
    def is_level_unlocked(
        self,
        user_id: str,
        project_id: str,
        level_id: str
    ) -> bool:
        """
        Check if a level is unlocked for the user
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            level_id: Level identifier
        
        Returns:
            True if level is unlocked, False otherwise
        """
        key = f"{user_id}:{project_id}"
        
        if key not in self._project_progress:
            return False
        
        project_progress = self._project_progress[key]
        
        # First level is always unlocked
        if project_progress.level_progress and level_id == project_progress.level_progress[0].level_id:
            return True
        
        # Find the level
        level_index = None
        for i, lp in enumerate(project_progress.level_progress):
            if lp.level_id == level_id:
                level_index = i
                break
        
        if level_index is None or level_index == 0:
            return False
        
        # Check if previous level is completed
        previous_level = project_progress.level_progress[level_index - 1]
        return previous_level.status == LevelStatus.COMPLETED
    
    def get_all_user_projects(self, user_id: str) -> List[ProjectProgress]:
        """
        Get all projects for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            List of ProjectProgress
        """
        return [
            progress for key, progress in self._project_progress.items()
            if progress.user_id == user_id
        ]


# ============================================
# Example Usage & Demo
# ============================================

if __name__ == '__main__':
    from app.models.core import Level, Challenge, ChallengeType, Difficulty
    from app.services.models import ChallengeResult
    
    print("="*60)
    print("Progress Service Demo")
    print("="*60)
    
    # Create service
    service = ProgressService()
    
    # Create sample levels
    level1 = Level(
        id="level-1",
        name="Understanding Flask Routes",
        description="Learn how Flask routing works",
        difficulty=Difficulty.BASIC,
        entry_function="index",
        call_chain=["index", "route"],
        code_snippet="# Flask code",
        challenges=[
            Challenge(
                id="c1",
                type=ChallengeType.MULTIPLE_CHOICE,
                question={"prompt": "What is WSGI?"},
                answer={"correct": "Web Server Gateway Interface"},
                hints=["It's a standard"],
                points=10
            ),
            Challenge(
                id="c2",
                type=ChallengeType.CODE_TRACING,
                question={"prompt": "Trace the call"},
                answer={"chain": ["index", "route"]},
                hints=["Start with index"],
                points=15
            )
        ],
        objectives=["Understand routing"],
        xp_reward=100,
        estimated_time=10,
        prerequisites=[]
    )
    
    level2 = Level(
        id="level-2",
        name="Flask Request Handling",
        description="Learn request handling",
        difficulty=Difficulty.INTERMEDIATE,
        entry_function="handle_request",
        call_chain=["handle_request", "parse"],
        code_snippet="# Request code",
        challenges=[
            Challenge(
                id="c3",
                type=ChallengeType.FILL_BLANK,
                question={"prompt": "Complete the code"},
                answer={"fill": "request.args"},
                hints=["Use request object"],
                points=12
            )
        ],
        objectives=["Handle requests"],
        xp_reward=150,
        estimated_time=15,
        prerequisites=["level-1"]
    )
    
    # Initialize project
    print("\n1. Initializing project...")
    user_id = "user-123"
    project_id = "mini-flask"
    
    progress = service.initialize_project(
        user_id, project_id, "Mini Flask", [level1, level2]
    )
    
    print(f"   Project: {progress.project_name}")
    print(f"   Total Levels: {progress.total_levels}")
    print(f"   Completion: {progress.completion_percentage:.1f}%")
    
    # Start level 1
    print("\n2. Starting Level 1...")
    lp1 = service.start_level(user_id, project_id, "level-1")
    print(f"   Status: {lp1.status.value}")
    print(f"   Started: {lp1.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Complete level 1
    print("\n3. Completing Level 1...")
    result = LevelResult(
        level_id="level-1",
        level_completed=True,
        score=25,
        max_score=25,
        challenge_results=[
            ChallengeResult("c1", True, 10, 10, "Correct!"),
            ChallengeResult("c2", True, 15, 15, "Perfect trace!")
        ],
        time_taken=300,  # 5 minutes
        hints_used=0,
        is_first_attempt=True,
        is_perfect_score=True
    )
    
    lp1 = service.complete_level(user_id, project_id, "level-1", result)
    print(f"   Best Score: {lp1.best_score}/{lp1.max_score}")
    print(f"   Status: {lp1.status.value}")
    print(f"   Perfect: {lp1.is_perfect}")
    
    # Unlock next level
    print("\n4. Unlocking Next Level...")
    next_level_id = service.unlock_next_level(user_id, project_id, "level-1")
    print(f"   Next Level: {next_level_id}")
    print(f"   Is Unlocked: {service.is_level_unlocked(user_id, project_id, next_level_id)}")
    
    # Check project progress
    print("\n5. Project Progress...")
    progress = service.get_user_progress(user_id, project_id)
    print(f"   Completed: {progress.completed_levels}/{progress.total_levels}")
    print(f"   Percentage: {progress.completion_percentage:.1f}%")
    print(f"   Average Score: {progress.average_score:.1f}%")
    print(f"   Time Spent: {progress.total_time_spent}s")
    
    print("\n" + "="*60)
    print("✓ Progress Service is working!")
    print("="*60)
