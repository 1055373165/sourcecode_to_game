"""
Leaderboard Service

Manages user rankings and leaderboards for competition and motivation.
Supports global, weekly, and project-specific leaderboards.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

from app.services.models import LeaderboardEntry, UserStats


class LeaderboardService:
    """
    Service for managing leaderboards
    
    Leaderboard Types:
    - Global: All-time XP ranking
    - Weekly: XP earned this week
    - Project: Top scores for a specific project
    """
    
    def __init__(self):
        # In-memory storage (would be database/Redis in production)
        self._user_stats_cache: Dict[str, UserStats] = {}
        self._weekly_xp: Dict[str, int] = {}  # user_id -> weekly XP
        self._project_scores: Dict[str, Dict[str, int]] = {}  # project_id -> {user_id -> score}
        self._user_info: Dict[str, Dict] = {}  # user_id -> {username, avatar}
    
    def register_user(self, user_id: str, username: str, avatar: str = None) -> None:
        """
        Register user information for leaderboards
        
        Args:
            user_id: User identifier
            username: Display name
            avatar: Avatar URL (optional)
        """
        self._user_info[user_id] = {
            "username": username,
            "avatar": avatar
        }
    
    def update_user_stats(self, user_id: str, user_stats: UserStats) -> None:
        """
        Update cached user stats
        
        Args:
            user_id: User identifier
            user_stats: Updated user statistics
        """
        self._user_stats_cache[user_id] = user_stats
    
    def record_weekly_xp(self, user_id: str, xp_earned: int) -> None:
        """
        Record XP earned this week
        
        Args:
            user_id: User identifier
            xp_earned: Amount of XP earned
        """
        if user_id not in self._weekly_xp:
            self._weekly_xp[user_id] = 0
        self._weekly_xp[user_id] += xp_earned
    
    def record_project_score(self, user_id: str, project_id: str, score: int) -> None:
        """
        Record user's score for a project
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            score: Total score for project
        """
        if project_id not in self._project_scores:
            self._project_scores[project_id] = {}
        
        # Only update if better than previous score
        current = self._project_scores[project_id].get(user_id, 0)
        self._project_scores[project_id][user_id] = max(current, score)
    
    def get_global_leaderboard(self, limit: int = 50) -> List[LeaderboardEntry]:
        """
        Get global leaderboard (all-time XP)
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of leaderboard entries, sorted by XP
        """
        # Get all users with stats
        entries = []
        for user_id, stats in self._user_stats_cache.items():
            user_info = self._user_info.get(user_id, {})
            entries.append({
                "user_id": user_id,
                "username": user_info.get("username", f"User {user_id[:8]}"),
                "avatar": user_info.get("avatar"),
                "score": stats.total_xp,
                "level": stats.current_level
            })
        
        # Sort by XP (descending)
        entries.sort(key=lambda x: x["score"], reverse=True)
        
        # Assign ranks and create LeaderboardEntry objects
        leaderboard = []
        for rank, entry in enumerate(entries[:limit], start=1):
            leaderboard.append(LeaderboardEntry(
                rank=rank,
                user_id=entry["user_id"],
                username=entry["username"],
                score=entry["score"],
                avatar=entry["avatar"],
                level=entry["level"]
            ))
        
        return leaderboard
    
    def get_weekly_leaderboard(self, limit: int = 50) -> List[LeaderboardEntry]:
        """
        Get weekly leaderboard (XP earned this week)
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of leaderboard entries, sorted by weekly XP
        """
        # Get all users with weekly XP
        entries = []
        for user_id, weekly_xp in self._weekly_xp.items():
            user_info = self._user_info.get(user_id, {})
            stats = self._user_stats_cache.get(user_id)
            
            entries.append({
                "user_id": user_id,
                "username": user_info.get("username", f"User {user_id[:8]}"),
                "avatar": user_info.get("avatar"),
                "score": weekly_xp,
                "level": stats.current_level if stats else None
            })
        
        # Sort by weekly XP (descending)
        entries.sort(key=lambda x: x["score"], reverse=True)
        
        # Assign ranks
        leaderboard = []
        for rank, entry in enumerate(entries[:limit], start=1):
            leaderboard.append(LeaderboardEntry(
                rank=rank,
                user_id=entry["user_id"],
                username=entry["username"],
                score=entry["score"],
                avatar=entry["avatar"],
                level=entry["level"]
            ))
        
        return leaderboard
    
    def get_project_leaderboard(
        self,
        project_id: str,
        limit: int = 50
    ) -> List[LeaderboardEntry]:
        """
        Get project-specific leaderboard
        
        Args:
            project_id: Project identifier
            limit: Maximum number of entries to return
        
        Returns:
            List of leaderboard entries, sorted by project score
        """
        project_scores = self._project_scores.get(project_id, {})
        
        # Get all users with scores for this project
        entries = []
        for user_id, score in project_scores.items():
            user_info = self._user_info.get(user_id, {})
            stats = self._user_stats_cache.get(user_id)
            
            entries.append({
                "user_id": user_id,
                "username": user_info.get("username", f"User {user_id[:8]}"),
                "avatar": user_info.get("avatar"),
                "score": score,
                "level": stats.current_level if stats else None
            })
        
        # Sort by score (descending)
        entries.sort(key=lambda x: x["score"], reverse=True)
        
        # Assign ranks
        leaderboard = []
        for rank, entry in enumerate(entries[:limit], start=1):
            leaderboard.append(LeaderboardEntry(
                rank=rank,
                user_id=entry["user_id"],
                username=entry["username"],
                score=entry["score"],
                avatar=entry["avatar"],
                level=entry["level"]
            ))
        
        return leaderboard
    
    def get_user_rank(
        self,
        user_id: str,
        leaderboard_type: str = "global",
        project_id: Optional[str] = None
    ) -> int:
        """
        Get user's rank in a specific leaderboard
        
        Args:
            user_id: User identifier
            leaderboard_type: "global", "weekly", or "project"
            project_id: Required if leaderboard_type is "project"
        
        Returns:
            User's rank (1-based), or 0 if not ranked
        """
        if leaderboard_type == "global":
            leaderboard = self.get_global_leaderboard(limit=10000)
        elif leaderboard_type == "weekly":
            leaderboard = self.get_weekly_leaderboard(limit=10000)
        elif leaderboard_type == "project":
            if not project_id:
                return 0
            leaderboard = self.get_project_leaderboard(project_id, limit=10000)
        else:
            return 0
        
        # Find user's rank
        for entry in leaderboard:
            if entry.user_id == user_id:
                return entry.rank
        
        return 0  # Not ranked
    
    def reset_weekly_leaderboard(self) -> None:
        """
        Reset weekly XP (should be called weekly via cron job)
        """
        self._weekly_xp.clear()


# ============================================
# Example Usage & Demo
# ============================================

if __name__ == '__main__':
    print("="*60)
    print("Leaderboard Service Demo")
    print("="*60)
    
    # Create service
    service = LeaderboardService()
    
    # Register users
    users = [
        ("user-1", "Alice", "avatar1.jpg"),
        ("user-2", "Bob", "avatar2.jpg"),
        ("user-3", "Charlie", "avatar3.jpg"),
        ("user-4", "Diana", "avatar4.jpg"),
        ("user-5", "Eve", "avatar5.jpg"),
    ]
    
    for user_id, username, avatar in users:
        service.register_user(user_id, username, avatar)
    
    # Create user stats with different XP
    xp_values = [1500, 2500, 800, 3200, 1200]
    for i, (user_id, _, _) in enumerate(users):
        stats = UserStats(
            user_id=user_id,
            total_xp=xp_values[i],
            current_level=(xp_values[i] // 500) + 1,
            levels_completed=xp_values[i] // 100
        )
        service.update_user_stats(user_id, stats)
    
    # Record weekly XP
    weekly_xp_values = [300, 500, 150, 700, 250]
    for i, (user_id, _, _) in enumerate(users):
        service.record_weekly_xp(user_id, weekly_xp_values[i])
    
    # Record project scores
    project_scores = [85, 92, 78, 95, 88]
    for i, (user_id, _, _) in enumerate(users):
        service.record_project_score(user_id, "mini-flask", project_scores[i])
    
    # Get global leaderboard
    print("\n🏆 Global Leaderboard (All-Time XP):")
    print(f"{'Rank':<6} {'Username':<12} {'Level':<7} {'XP':<10}")
    print("-" * 40)
    
    global_board = service.get_global_leaderboard(limit=10)
    for entry in global_board:
        print(f"{entry.rank:<6} {entry.username:<12} L{entry.level:<6} {entry.score:<10,}")
    
    # Get weekly leaderboard
    print("\n📅 Weekly Leaderboard:")
    print(f"{'Rank':<6} {'Username':<12} {'XP This Week':<15}")
    print("-" * 40)
    
    weekly_board = service.get_weekly_leaderboard(limit=10)
    for entry in weekly_board:
        print(f"{entry.rank:<6} {entry.username:<12} {entry.score:<15,}")
    
    # Get project leaderboard
    print("\n🎯 Mini-Flask Project Leaderboard:")
    print(f"{'Rank':<6} {'Username':<12} {'Score':<10}")
    print("-" * 40)
    
    project_board = service.get_project_leaderboard("mini-flask", limit=10)
    for entry in project_board:
        print(f"{entry.rank:<6} {entry.username:<12} {entry.score:<10}")
    
    # Get user rank
    print("\n🔍 User Rankings:")
    for user_id, username, _ in users[:3]:
        global_rank = service.get_user_rank(user_id, "global")
        weekly_rank = service.get_user_rank(user_id, "weekly")
        project_rank = service.get_user_rank(user_id, "project", "mini-flask")
        
        print(f"   {username}:")
        print(f"     Global: #{global_rank}")
        print(f"     Weekly: #{weekly_rank}")
        print(f"     Mini-Flask: #{project_rank}")
    
    print("\n" + "="*60)
    print("✓ Leaderboard Service is working!")
    print("="*60)
