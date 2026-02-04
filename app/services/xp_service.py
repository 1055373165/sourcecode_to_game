"""
XP and Leveling Service

Handles experience points, user leveling, and streak tracking.
Implements the gamification core that motivates users.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict
from app.services.models import UserStats, XPAward, LevelUp


class XPService:
    """
    Service for managing user XP, levels, and streaks
    
    Leveling Formula: XP needed for level N = 100 * N^1.5
    
    XP Sources:
    - Level completion: 50-300 XP (based on difficulty)
    - Perfect score bonus: +50% XP
    - First attempt bonus: +25% XP
    - Daily streak bonus: +10% XP per day (max 50%)
    """
    
    def __init__(self):
        # In-memory storage (would be database in production)
        self._user_stats: Dict[str, UserStats] = {}
    
    def get_user_stats(self, user_id: str) -> UserStats:
        """
        Get user statistics, creating if doesn't exist
        
        Args:
            user_id: User identifier
        
        Returns:
            UserStats object
        """
        if user_id not in self._user_stats:
            self._user_stats[user_id] = UserStats(user_id=user_id)
        
        return self._user_stats[user_id]
    
    def award_xp(
        self,
        user_id: str,
        base_xp: int,
        is_perfect: bool = False,
        is_first_attempt: bool = False,
        reason: str = "Level completion"
    ) -> tuple[XPAward, Optional[LevelUp]]:
        """
        Award XP to a user with bonuses
        
        Args:
            user_id: User identifier
            base_xp: Base XP amount
            is_perfect: Whether user got perfect score
            is_first_attempt: Whether this is first attempt
            reason: Reason for award
        
        Returns:
            Tuple of (XPAward, Optional[LevelUp])
        """
        stats = self.get_user_stats(user_id)
        
        # Update streak
        current_streak = self.update_streak(user_id)
        
        # Calculate bonuses
        breakdown = {"base": base_xp}
        total_xp = base_xp
        
        # Perfect score bonus (+50%)
        if is_perfect:
            perfect_bonus = int(base_xp * 0.5)
            breakdown["perfect_bonus"] = perfect_bonus
            total_xp += perfect_bonus
        
        # First attempt bonus (+25%)
        if is_first_attempt:
            first_attempt_bonus = int(base_xp * 0.25)
            breakdown["first_attempt_bonus"] = first_attempt_bonus
            total_xp += first_attempt_bonus
        
        # Streak bonus (+10% per day, max 50%)
        if current_streak > 1:
            streak_multiplier = min(0.5, (current_streak - 1) * 0.1)
            streak_bonus = int(base_xp * streak_multiplier)
            breakdown["streak_bonus"] = streak_bonus
            breakdown["streak_days"] = current_streak
            total_xp += streak_bonus
        
        # Award XP
        stats.total_xp += total_xp
        
        # Create award record
        xp_award = XPAward(
            amount=total_xp,
            reason=reason,
            breakdown=breakdown
        )
        
        # Check for level up
        level_up = self.check_levelup(user_id)
        
        return xp_award, level_up
    
    def calculate_level_xp(self, level: int) -> int:
        """
        Calculate XP required to reach a level
        
        Formula: 100 * N^1.5
        
        Args:
            level: Target level
        
        Returns:
            XP required
        """
        return int(100 * (level ** 1.5))
    
    def check_levelup(self, user_id: str) -> Optional[LevelUp]:
        """
        Check if user should level up
        
        Args:
            user_id: User identifier
        
        Returns:
            LevelUp if user leveled up, None otherwise
        """
        stats = self.get_user_stats(user_id)
        
        old_level = stats.current_level
        new_level = old_level
        
        # Keep leveling up until XP requirement not met
        while True:
            xp_needed = self.calculate_level_xp(new_level + 1)
            
            if stats.total_xp >= xp_needed:
                new_level += 1
            else:
                break
        
        # Update if leveled up
        if new_level > old_level:
            stats.current_level = new_level
            stats.xp_to_next_level = self.calculate_level_xp(new_level + 1)
            
            # Generate rewards
            rewards = self._generate_level_rewards(new_level)
            
            return LevelUp(
                old_level=old_level,
                new_level=new_level,
                xp_to_next=stats.xp_to_next_level,
                rewards=rewards
            )
        
        # Update XP to next level
        stats.xp_to_next_level = self.calculate_level_xp(stats.current_level + 1) - stats.total_xp
        
        return None
    
    def _generate_level_rewards(self, level: int) -> list[str]:
        """
        Generate rewards for reaching a level
        
        Args:
            level: Level reached
        
        Returns:
            List of reward descriptions
        """
        rewards = []
        
        # Milestone rewards
        if level == 5:
            rewards.append("🎓 Badge: Rising Star")
        elif level == 10:
            rewards.append("🌟 Badge: Code Warrior")
        elif level == 20:
            rewards.append("👑 Badge: Master Developer")
        elif level == 50:
            rewards.append("💎 Badge: Legendary Coder")
        
        # Every 10 levels: bonus XP
        if level % 10 == 0:
            rewards.append(f"💰 Bonus: {level * 10} XP")
        
        # Every 5 levels: hint pack
        if level % 5 == 0:
            rewards.append("💡 Item: 3 Free Hints")
        
        return rewards
    
    def update_streak(self, user_id: str) -> int:
        """
        Update user's activity streak
        
        Args:
            user_id: User identifier
        
        Returns:
            Current streak count
        """
        stats = self.get_user_stats(user_id)
        today = date.today()
        
        if stats.last_activity_date is None:
            # First activity
            stats.current_streak = 1
            stats.longest_streak = 1
            stats.last_activity_date = datetime.now()
        else:
            last_date = stats.last_activity_date.date()
            days_diff = (today - last_date).days
            
            if days_diff == 0:
                # Same day, streak continues
                pass
            elif days_diff == 1:
                # Next day, increment streak
                stats.current_streak += 1
                stats.last_activity_date = datetime.now()
                
                # Update longest streak
                if stats.current_streak > stats.longest_streak:
                    stats.longest_streak = stats.current_streak
            else:
                # Streak broken
                stats.current_streak = 1
                stats.last_activity_date = datetime.now()
        
        return stats.current_streak
    
    def get_user_rank(self, user_id: str) -> int:
        """
        Get user's global rank by XP
        
        Args:
            user_id: User identifier
        
        Returns:
            Rank (1-based, 1 is highest)
        """
        stats = self.get_user_stats(user_id)
        
        # Sort all users by XP
        sorted_users = sorted(
            self._user_stats.values(),
            key=lambda x: x.total_xp,
            reverse=True
        )
        
        # Find user's rank
        for rank, user_stat in enumerate(sorted_users, start=1):
            if user_stat.user_id == user_id:
                return rank
        
        return len(sorted_users)
    
    def increment_stat(self, user_id: str, stat_name: str, amount: int = 1) -> None:
        """
        Increment a user statistic
        
        Args:
            user_id: User identifier
            stat_name: Name of stat (levels_completed, projects_completed, perfect_scores)
            amount: Amount to increment
        """
        stats = self.get_user_stats(user_id)
        
        if stat_name == "levels_completed":
            stats.levels_completed += amount
        elif stat_name == "projects_completed":
            stats.projects_completed += amount
        elif stat_name == "perfect_scores":
            stats.perfect_scores += amount
        elif stat_name == "time_spent":
            stats.total_time_spent += amount


# ============================================
# Example Usage & Demo
# ============================================

if __name__ == '__main__':
    print("="*60)
    print("XP Service Demo")
    print("="*60)
    
    # Create service
    service = XPService()
    user_id = "user-123"
    
    # Initial stats
    print("\n1. Initial Stats...")
    stats = service.get_user_stats(user_id)
    print(f"   Level: {stats.current_level}")
    print(f"   Total XP: {stats.total_xp}")
    print(f"   XP to Next: {stats.xp_to_next_level}")
    
    # Award XP for level completion
    print("\n2. Completing First Level (Perfect Score, First Attempt)...")
    xp_award, level_up = service.award_xp(
        user_id,
        base_xp=100,
        is_perfect=True,
        is_first_attempt=True,
        reason="Completed 'Understanding Flask Routes'"
    )
    
    print(f"   XP Awarded: {xp_award.amount}")
    print(f"   Breakdown:")
    for source, amount in xp_award.breakdown.items():
        print(f"     - {source}: +{amount}")
    
    if level_up:
        print(f"   🎉 LEVEL UP! {level_up.old_level} → {level_up.new_level}")
        print(f"   XP to Next: {level_up.xp_to_next}")
        if level_up.rewards:
            print(f"   Rewards: {', '.join(level_up.rewards)}")
    
    stats = service.get_user_stats(user_id)
    print(f"   Current Level: {stats.current_level}")
    print(f"   Total XP: {stats.total_xp}")
    
    # Complete more levels
    print("\n3. Completing More Levels...")
    for i in range(5):
        xp_award, level_up = service.award_xp(
            user_id,
            base_xp=150,
            is_perfect=False,
            is_first_attempt=True,
            reason=f"Completed Level {i+2}"
        )
        
        print(f"   Level {i+2}: +{xp_award.amount} XP", end="")
        if level_up:
            print(f" → LEVEL UP to {level_up.new_level}!", end="")
        print()
    
    stats = service.get_user_stats(user_id)
    print(f"\n   Final Level: {stats.current_level}")
    print(f"   Total XP: {stats.total_xp}")
    print(f"   XP to Next: {stats.xp_to_next_level}")
    
    # Test streak system
    print("\n4. Testing Streak System...")
    stats.last_activity_date = datetime.now() - timedelta(days=1)
    stats.current_streak = 5
    
    xp_award, _ = service.award_xp(
        user_id,
        base_xp=100,
        is_perfect=False,
        is_first_attempt=False,
        reason="Daily activity"
    )
    
    print(f"   Current Streak: {stats.current_streak} days")
    print(f"   Streak Bonus: {xp_award.breakdown.get('streak_bonus', 0)} XP")
    print(f"   Total XP: +{xp_award.amount}")
    
    # XP requirements
    print("\n5. XP Requirements per Level...")
    for level in [1, 2, 3, 5, 10, 20, 50]:
        xp_needed = service.calculate_level_xp(level)
        print(f"   Level {level}: {xp_needed:,} XP")
    
    # User stats
    print("\n6. Final User Stats...")
    stats = service.get_user_stats(user_id)
    stats.levels_completed = 6
    stats.perfect_scores = 2
    
    print(f"   User ID: {stats.user_id}")
    print(f"   Level: {stats.current_level}")
    print(f"   Total XP: {stats.total_xp:,}")
    print(f"   Levels Completed: {stats.levels_completed}")
    print(f"   Perfect Scores: {stats.perfect_scores}")
    print(f"   Current Streak: {stats.current_streak} days")
    print(f"   Longest Streak: {stats.longest_streak} days")
    
    print("\n" + "="*60)
    print("✓ XP Service is working!")
    print("="*60)
