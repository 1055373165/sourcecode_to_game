"""
Achievement System - Default Achievements Definition

Predefined achievements that users can unlock through gameplay.
"""

from app.services.models import Achievement, AchievementCategory

# All available achievements
DEFAULT_ACHIEVEMENTS = [
    # ==========================================
    # PROGRESSION ACHIEVEMENTS
    # ==========================================
    Achievement(
        id="first_steps",
        name="🎓 First Steps",
        description="Complete your first level",
        icon="🎓",
        category=AchievementCategory.PROGRESSION,
        xp_reward=50,
        condition={"type": "levels_completed", "count": 1}
    ),
    Achievement(
        id="rising_star",
        name="🌟 Rising Star",
        description="Complete 5 levels",
        icon="🌟",
        category=AchievementCategory.PROGRESSION,
        xp_reward=100,
        condition={"type": "levels_completed", "count": 5}
    ),
    Achievement(
        id="dedicated_learner",
        name="📚 Dedicated Learner",
        description="Complete 10 levels",
        icon="📚",
        category=AchievementCategory.PROGRESSION,
        xp_reward=200,
        condition={"type": "levels_completed", "count": 10}
    ),
    Achievement(
        id="code_warrior",
        name="⚔️ Code Warrior",
        description="Complete 25 levels",
        icon="⚔️",
        category=AchievementCategory.PROGRESSION,
        xp_reward=500,
        condition={"type": "levels_completed", "count": 25}
    ),
    Achievement(
        id="master_explorer",
        name="🗺️ Master Explorer",
        description="Complete 50 levels",
        icon="🗺️",
        category=AchievementCategory.PROGRESSION,
        xp_reward=1000,
        condition={"type": "levels_completed", "count": 50}
    ),
    Achievement(
        id="project_starter",
        name="🚀 Project Starter",
        description="Complete your first project",
        icon="🚀",
        category=AchievementCategory.PROGRESSION,
        xp_reward=300,
        condition={"type": "projects_completed", "count": 1}
    ),
    Achievement(
        id="framework_master",
        name="👑 Framework Master",
        description="Complete 3 projects",
        icon="👑",
        category=AchievementCategory.PROGRESSION,
        xp_reward=1000,
        condition={"type": "projects_completed", "count": 3}
    ),
    
    # ==========================================
    # PERFORMANCE ACHIEVEMENTS
    # ==========================================
    Achievement(
        id="perfectionist",
        name="🎯 Perfectionist",
        description="Get 100% score on a level",
        icon="🎯",
        category=AchievementCategory.PERFORMANCE,
        xp_reward=100,
        condition={"type": "perfect_scores", "count": 1}
    ),
    Achievement(
        id="flawless_five",
        name="💎 Flawless Five",
        description="Get perfect scores on 5 levels",
        icon="💎",
        category=AchievementCategory.PERFORMANCE,
        xp_reward=250,
        condition={"type": "perfect_scores", "count": 5}
    ),
    Achievement(
        id="perfection_streak",
        name="✨ Perfection Streak",
        description="Get perfect scores on 10 levels",
        icon="✨",
        category=AchievementCategory.PERFORMANCE,
        xp_reward=500,
        condition={"type": "perfect_scores", "count": 10}
    ),
    Achievement(
        id="speed_demon",
        name="⚡ Speed Demon",
        description="Complete a level in under 3 minutes",
        icon="⚡",
        category=AchievementCategory.PERFORMANCE,
        xp_reward=150,
        condition={"type": "fast_completion", "time": 180}
    ),
    Achievement(
        id="lightning_fast",
        name="🌩️ Lightning Fast",
        description="Complete 5 levels in under 3 minutes each",
        icon="🌩️",
        category=AchievementCategory.PERFORMANCE,
        xp_reward=400,
        condition={"type": "fast_completions", "count": 5, "time": 180}
    ),
    Achievement(
        id="first_try_master",
        name="🥇 First Try Master",
        description="Complete 10 levels on first attempt",
        icon="🥇",
        category=AchievementCategory.PERFORMANCE,
        xp_reward=300,
        condition={"type": "first_attempts", "count": 10}
    ),
    
    # ==========================================
    # SPECIAL ACHIEVEMENTS
    # ==========================================
    Achievement(
        id="framework_architect",
        name="🏗️ Framework Architect",
        description="Complete a mini project implementation",
        icon="🏗️",
        category=AchievementCategory.SPECIAL,
        xp_reward=1000,
        condition={"type": "mini_projects", "count": 1}
    ),
    Achievement(
        id="early_bird",
        name="🌅 Early Bird",
        description="Complete a level before 8 AM",
        icon="🌅",
        category=AchievementCategory.SPECIAL,
        xp_reward=100,
        condition={"type": "early_completion", "hour": 8}
    ),
    Achievement(
        id="night_owl",
        name="🦉 Night Owl",
        description="Complete a level after 10 PM",
        icon="🦉",
        category=AchievementCategory.SPECIAL,
        xp_reward=100,
        condition={"type": "late_completion", "hour": 22}
    ),
    Achievement(
        id="weekend_warrior",
        name="🎮 Weekend Warrior",
        description="Complete 5 levels on a weekend",
        icon="🎮",
        category=AchievementCategory.SPECIAL,
        xp_reward=200,
        condition={"type": "weekend_levels", "count": 5}
    ),
    Achievement(
        id="consistent_learner",
        name="📅 Consistent Learner",
        description="Maintain a 7-day streak",
        icon="📅",
        category=AchievementCategory.SPECIAL,
        xp_reward=300,
        condition={"type": "streak", "days": 7}
    ),
    Achievement(
        id="dedication_master",
        name="🔥 Dedication Master",
        description="Maintain a 30-day streak",
        icon="🔥",
        category=AchievementCategory.SPECIAL,
        xp_reward=1000,
        condition={"type": "streak", "days": 30}
    ),
    Achievement(
        id="challenge_accepted",
        name="💪 Challenge Accepted",
        description="Complete an Expert difficulty level",
        icon="💪",
        category=AchievementCategory.SPECIAL,
        xp_reward=500,
        condition={"type": "difficulty_level", "difficulty": "EXPERT"}
    ),
]


def get_achievement_by_id(achievement_id: str) -> Achievement:
    """Get achievement by ID"""
    for achievement in DEFAULT_ACHIEVEMENTS:
        if achievement.id == achievement_id:
            return achievement
    return None


def get_achievements_by_category(category: AchievementCategory) -> list[Achievement]:
    """Get all achievements in a category"""
    return [a for a in DEFAULT_ACHIEVEMENTS if a.category == category]


def get_all_achievements() -> list[Achievement]:
    """Get all available achievements"""
    return DEFAULT_ACHIEVEMENTS.copy()
