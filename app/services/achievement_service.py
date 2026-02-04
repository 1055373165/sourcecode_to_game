"""
Achievement Service

Manages achievement unlocking, tracking, and rewards.
Checks user actions against achievement conditions and awards badges.
"""

from datetime import datetime
from typing import List, Dict, Set, Optional

from app.services.models import Achievement, AchievementCategory, UserStats
from app.services.achievements.default_achievements import (
    DEFAULT_ACHIEVEMENTS, get_achievement_by_id, get_all_achievements
)


class AchievementService:
    """
    Service for managing achievements
    
    Responsibilities:
    - Check if user unlocked achievements
    - Award achievements and XP rewards
    - Track user's unlocked achievements
    - Provide achievement progress information
    """
    
    def __init__(self):
        # In-memory storage (would be database in production)
        self._user_achievements: Dict[str, Set[str]] = {}  # user_id -> set of achievement_ids
        self._achievement_unlock_times: Dict[str, datetime] = {}  # "user:achievement" -> datetime
    
    def check_achievements(
        self,
        user_id: str,
        user_stats: UserStats,
        event_type: str,
        event_data: Dict = None
    ) -> List[Achievement]:
        """
        Check if user unlocked any new achievements
        
        Args:
            user_id: User identifier
            user_stats: Current user statistics
            event_type: Type of event that triggered check
            event_data: Additional event data
        
        Returns:
            List of newly unlocked achievements
        """
        if event_data is None:
            event_data = {}
        
        newly_unlocked = []
        
        for achievement in DEFAULT_ACHIEVEMENTS:
            # Skip if already unlocked
            if self.is_unlocked(user_id, achievement.id):
                continue
            
            # Check if conditions are met
            if self._check_condition(achievement, user_stats, event_type, event_data):
                self._unlock_achievement(user_id, achievement.id)
                newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def _check_condition(
        self,
        achievement: Achievement,
        user_stats: UserStats,
        event_type: str,
        event_data: Dict
    ) -> bool:
        """
        Check if achievement condition is met
        
        Args:
            achievement: Achievement to check
            user_stats: User statistics
            event_type: Event type
            event_data: Event data
        
        Returns:
            True if condition met, False otherwise
        """
        condition = achievement.condition
        condition_type = condition.get("type")
        
        # Progression achievements
        if condition_type == "levels_completed":
            return user_stats.levels_completed >= condition.get("count", 0)
        
        elif condition_type == "projects_completed":
            return user_stats.projects_completed >= condition.get("count", 0)
        
        # Performance achievements
        elif condition_type == "perfect_scores":
            return user_stats.perfect_scores >= condition.get("count", 0)
        
        elif condition_type == "fast_completion":
            if event_type == "level_completed":
                time_taken = event_data.get("time_taken", float('inf'))
                return time_taken <= condition.get("time", 0)
            return False
        
        elif condition_type == "fast_completions":
            # Would need to track this separately in production
            return False  # Simplified for MVP
        
        elif condition_type == "first_attempts":
            # Would need to track this separately in production
            return False  # Simplified for MVP
        
        # Special achievements
        elif condition_type == "mini_projects":
            # Would check mini_projects_completed in production
            return False  # Simplified for MVP
        
        elif condition_type == "streak":
            return user_stats.current_streak >= condition.get("days", 0)
        
        elif condition_type == "early_completion":
            if event_type == "level_completed":
                completion_time = event_data.get("completed_at", datetime.now())
                return completion_time.hour < condition.get("hour", 24)
            return False
        
        elif condition_type == "late_completion":
            if event_type == "level_completed":
                completion_time = event_data.get("completed_at", datetime.now())
                return completion_time.hour >= condition.get("hour", 0)
            return False
        
        elif condition_type == "weekend_levels":
            # Would need separate tracking
            return False  # Simplified for MVP
        
        elif condition_type == "difficulty_level":
            if event_type == "level_completed":
                difficulty = event_data.get("difficulty", "")
                return difficulty == condition.get("difficulty", "")
            return False
        
        return False
    
    def _unlock_achievement(self, user_id: str, achievement_id: str) -> None:
        """
        Unlock an achievement for a user
        
        Args:
            user_id: User identifier
            achievement_id: Achievement identifier
        """
        if user_id not in self._user_achievements:
            self._user_achievements[user_id] = set()
        
        self._user_achievements[user_id].add(achievement_id)
        
        key = f"{user_id}:{achievement_id}"
        self._achievement_unlock_times[key] = datetime.now()
    
    def is_unlocked(self, user_id: str, achievement_id: str) -> bool:
        """
        Check if user has unlocked an achievement
        
        Args:
            user_id: User identifier
            achievement_id: Achievement identifier
        
        Returns:
            True if unlocked, False otherwise
        """
        return achievement_id in self._user_achievements.get(user_id, set())
    
    def get_user_achievements(self, user_id: str) -> List[Achievement]:
        """
        Get all achievements unlocked by user
        
        Args:
            user_id: User identifier
        
        Returns:
            List of unlocked achievements with unlock times
        """
        unlocked_ids = self._user_achievements.get(user_id, set())
        
        achievements = []
        for achievement_id in unlocked_ids:
            achievement = get_achievement_by_id(achievement_id)
            if achievement:
                # Set unlock time
                key = f"{user_id}:{achievement_id}"
                achievement.unlocked_at = self._achievement_unlock_times.get(key)
                achievements.append(achievement)
        
        # Sort by unlock time (newest first)
        achievements.sort(key=lambda a: a.unlocked_at or datetime.min, reverse=True)
        
        return achievements
    
    def get_unlockable_achievements(
        self,
        user_id: str,
        user_stats: UserStats
    ) -> List[tuple[Achievement, float]]:
        """
        Get achievements that are close to being unlocked
        
        Args:
            user_id: User identifier
            user_stats: User statistics
        
        Returns:
            List of (achievement, progress_percentage) tuples
        """
        unlockable = []
        
        for achievement in DEFAULT_ACHIEVEMENTS:
            # Skip if already unlocked
            if self.is_unlocked(user_id, achievement.id):
                continue
            
            # Calculate progress
            progress = self._calculate_progress(achievement, user_stats)
            
            # Only include if some progress made (>0%) and not complete (=100%)
            if 0 < progress < 100:
                unlockable.append((achievement, progress))
        
        # Sort by progress (closest to completion first)
        unlockable.sort(key=lambda x: x[1], reverse=True)
        
        return unlockable
    
    def _calculate_progress(self, achievement: Achievement, user_stats: UserStats) -> float:
        """
        Calculate progress toward an achievement
        
        Args:
            achievement: Achievement to check
            user_stats: User statistics
        
        Returns:
            Progress percentage (0-100)
        """
        condition = achievement.condition
        condition_type = condition.get("type")
        
        if condition_type == "levels_completed":
            target = condition.get("count", 1)
            current = user_stats.levels_completed
            return min(100, (current / target) * 100)
        
        elif condition_type == "projects_completed":
            target = condition.get("count", 1)
            current = user_stats.projects_completed
            return min(100, (current / target) * 100)
        
        elif condition_type == "perfect_scores":
            target = condition.get("count", 1)
            current = user_stats.perfect_scores
            return min(100, (current / target) * 100)
        
        elif condition_type == "streak":
            target = condition.get("days", 1)
            current = user_stats.current_streak
            return min(100, (current / target) * 100)
        
        # For event-based achievements, can't calculate progress
        return 0.0
    
    def get_achievement_stats(self, user_id: str) -> Dict:
        """
        Get achievement statistics for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            Dictionary with achievement stats
        """
        unlocked = self._user_achievements.get(user_id, set())
        total = len(DEFAULT_ACHIEVEMENTS)
        
        # Count by category
        by_category = {}
        for achievement in DEFAULT_ACHIEVEMENTS:
            category = achievement.category.value
            by_category.setdefault(category, {"total": 0, "unlocked": 0})
            by_category[category]["total"] += 1
            if achievement.id in unlocked:
                by_category[category]["unlocked"] += 1
        
        # Calculate total XP from achievements
        total_achievement_xp = sum(
            get_achievement_by_id(aid).xp_reward
            for aid in unlocked
            if get_achievement_by_id(aid)
        )
        
        return {
            "total_achievements": total,
            "unlocked_count": len(unlocked),
            "completion_percentage": (len(unlocked) / total * 100) if total > 0 else 0,
            "by_category": by_category,
            "total_xp_earned": total_achievement_xp
        }


# ============================================
# Example Usage & Demo
# ============================================

if __name__ == '__main__':
    print("="*60)
    print("Achievement Service Demo")
    print("="*60)
    
    # Create service
    service = AchievementService()
    user_id = "test-user-789"
    
    # Create user stats
    user_stats = UserStats(
        user_id=user_id,
        total_xp=500,
        current_level=3,
        levels_completed=5,
        projects_completed=0,
        perfect_scores=2,
        current_streak=3
    )
    
    print(f"\n📊 User Stats:")
    print(f"   Levels Completed: {user_stats.levels_completed}")
    print(f"   Perfect Scores: {user_stats.perfect_scores}")
    print(f"   Current Streak: {user_stats.current_streak} days")
    
    # Check for unlocked achievements (level completion)
    print(f"\n🏆 Checking Achievements...")
    unlocked = service.check_achievements(
        user_id,
        user_stats,
        event_type="level_completed",
        event_data={"time_taken": 150, "completed_at": datetime.now()}
    )
    
    print(f"\n✨ Newly Unlocked: {len(unlocked)} achievements")
    for achievement in unlocked:
        print(f"   {achievement.icon} {achievement.name}")
        print(f"      XP Reward: +{achievement.xp_reward}")
        print(f"      {achievement.description}")
    
    # Get all user achievements
    print(f"\n📜 All Unlocked Achievements:")
    all_achievements = service.get_user_achievements(user_id)
    for achievement in all_achievements:
        print(f"   {achievement.icon} {achievement.name} (unlocked: {achievement.unlocked_at.strftime('%Y-%m-%d %H:%M')})")
    
    # Get unlockable achievements
    print(f"\n🎯 Close to Unlocking:")
    unlockable = service.get_unlockable_achievements(user_id, user_stats)
    for achievement, progress in unlockable[:5]:  # Top 5
        print(f"   {achievement.icon} {achievement.name}: {progress:.0f}%")
        print(f"      {achievement.description}")
    
    # Get achievement stats
    print(f"\n📈 Achievement Statistics:")
    stats = service.get_achievement_stats(user_id)
    print(f"   Unlocked: {stats['unlocked_count']}/{stats['total_achievements']} ({stats['completion_percentage']:.1f}%)")
    print(f"   Total XP from Achievements: {stats['total_xp_earned']}")
    print(f"\n   By Category:")
    for category, data in stats['by_category'].items():
        print(f"     {category}: {data['unlocked']}/{data['total']}")
    
    print("\n" + "="*60)
    print("✓ Achievement Service is working!")
    print("="*60)
