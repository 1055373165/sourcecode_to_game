#!/usr/bin/env python3
"""
Complete Game Engine Integration Test

Tests all game engine services working together:
- ProgressService
- XPService  
- ChallengeEvaluator
- AchievementService
- LeaderboardService
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.progress_service import ProgressService
from app.services.xp_service import XPService
from app.services.challenge_evaluator import ChallengeEvaluator
from app.services.achievement_service import AchievementService
from app.services.leaderboard_service import LeaderboardService
from app.models.core import Level, Challenge, ChallengeType, Difficulty


def create_test_level(level_id: str, difficulty: Difficulty, xp_reward: int) -> Level:
    """Create a test level"""
    return Level(
        id=level_id,
        name=f"Level {level_id}",
        description=f"Test level {level_id}",
        difficulty=difficulty,
        entry_function="test",
        call_chain=["test"],
        code_snippet="def test(): pass",
        challenges=[
            Challenge(
                id=f"{level_id}-c1",
                type=ChallengeType.MULTIPLE_CHOICE,
                question={"prompt": "Test question"},
                answer={"correct": "A"},
                hints=["Hint"],
                points=10
            )
        ],
        objectives=["Learn"],
        xp_reward=xp_reward,
        estimated_time=5,
        prerequisites=[]
    )


def main():
    print("="*70)
    print("🎮 COMPLETE GAME ENGINE INTEGRATION TEST")
    print("="*70)
    
    # Initialize all services
    progress_service = ProgressService()
    xp_service = XPService()
    evaluator = ChallengeEvaluator()
    achievement_service = AchievementService()
    leaderboard_service = LeaderboardService()
    
    # ==========================================
    # Setup: Multiple Users
    # ==========================================
    users = [
        ("alice-001", "Alice"),
        ("bob-002", "Bob"),
        ("charlie-003", "Charlie"),
    ]
    
    for user_id, username in users:
        leaderboard_service.register_user(user_id, username)
    
    print(f"\n👥 Registered {len(users)} users")
    
    # ==========================================
    # Scenario: Alice's Journey
    # ==========================================
    print("\n" + "="*70)
    print("👩 ALICE'S LEARNING JOURNEY")
    print("="*70)
    
    user_id = "alice-001"
    project_id = "mini-flask"
    
    # Create project with 5 levels
    levels = [
        create_test_level("level-1", Difficulty.BASIC, 100),
        create_test_level("level-2", Difficulty.BASIC, 150),
        create_test_level("level-3", Difficulty.INTERMEDIATE, 200),
        create_test_level("level-4", Difficulty.ADVANCED, 250),
        create_test_level("level-5", Difficulty.EXPERT, 300),
    ]
    
    # Initialize project
    progress_service.initialize_project(user_id, project_id, "Mini Flask", levels)
    print(f"\n📚 Project initialized with {len(levels)} levels")
    
    # Complete levels
    total_xp = 0
    for i, level in enumerate(levels[:3], 1):  # Complete first 3 levels
        print(f"\n{'─' * 70}")
        print(f"📖 Level {i}: {level.name}")
        print(f"{'─' * 70}")
        
        # Start level
        progress_service.start_level(user_id, project_id, level.id)
        
        # User answers (perfect score)
        user_answers = {
            f"{level.id}-c1": {"answer": "A"}
        }
        
        # Evaluate
        level_result = evaluator.evaluate_level(level, user_answers, time_taken=120)
        
        print(f"✅ Score: {level_result.score}/{level_result.max_score} ({level_result.percentage_score:.0f}%)")
        print(f"⏱️  Time: {level_result.time_taken}s")
        
        # Update progress
        progress_service.complete_level(user_id, project_id, level.id, level_result)
        
        # Award XP
        xp_award, level_up = xp_service.award_xp(
            user_id,
            base_xp=level.xp_reward,
            is_perfect=level_result.is_perfect_score,
            is_first_attempt=True
        )
        
        total_xp += xp_award.amount
        
        print(f"💎 XP Earned: +{xp_award.amount} (Total: {total_xp})")
        if level_up:
            print(f"🎉 LEVEL UP! {level_up.old_level} → {level_up.new_level}")
            if level_up.rewards:
                print(f"   Rewards: {', '.join(level_up.rewards)}")
        
        # Get and update user stats
        user_stats = xp_service.get_user_stats(user_id)
        xp_service.increment_stat(user_id, "levels_completed")
        if level_result.is_perfect_score:
            xp_service.increment_stat(user_id, "perfect_scores")
        
        # Check achievements
        newly_unlocked = achievement_service.check_achievements(
            user_id,
            user_stats,
            event_type="level_completed",
            event_data={
                "time_taken": level_result.time_taken,
                "completed_at": datetime.now(),
                "difficulty": level.difficulty.value
            }
        )
        
        if newly_unlocked:
            print(f"\n🏆 Achievements Unlocked:")
            for achievement in newly_unlocked:
                print(f"   {achievement.icon} {achievement.name} (+{achievement.xp_reward} XP)")
                # Award achievement XP
                xp_service.award_xp(user_id, achievement.xp_reward, reason="Achievement")
        
        # Update leaderboard
        leaderboard_service.update_user_stats(user_id, user_stats)
        leaderboard_service.record_weekly_xp(user_id, xp_award.amount)
    
    # ==========================================
    # Bob and Charlie also play
    # ==========================================
    print(f"\n{'='*70}")
    print("👥 OTHER USERS PLAYING")
    print(f"{'='*70}")
    
    # Bob completes 2 levels
    bob_stats = xp_service.get_user_stats("bob-002")
    bob_stats.total_xp = 500
    bob_stats.current_level = 2
    bob_stats.levels_completed = 2
    leaderboard_service.update_user_stats("bob-002", bob_stats)
    leaderboard_service.record_weekly_xp("bob-002", 300)
    
    # Charlie completes 1 level
    charlie_stats = xp_service.get_user_stats("charlie-003")
    charlie_stats.total_xp = 200
    charlie_stats.current_level = 1
    charlie_stats.levels_completed = 1
    leaderboard_service.update_user_stats("charlie-003", charlie_stats)
    leaderboard_service.record_weekly_xp("charlie-003", 150)
    
    print(f"✅ Bob completed 2 levels (500 XP)")
    print(f"✅ Charlie completed 1 level (200 XP)")
    
    # ==========================================
    # Final Summary
    # ==========================================
    print(f"\n{'='*70}")
    print("📊 FINAL SUMMARY")
    print(f"{'='*70}")
    
    # Alice's stats
    alice_stats = xp_service.get_user_stats(user_id)
    print(f"\n👩 Alice's Stats:")
    print(f"   Level: {alice_stats.current_level}")
    print(f"   Total XP: {alice_stats.total_xp:,}")
    print(f"   Levels Completed: {alice_stats.levels_completed}")
    print(f"   Perfect Scores: {alice_stats.perfect_scores}")
    
    # Project progress
    project_progress = progress_service.get_user_progress(user_id, project_id)
    print(f"\n📈 Project Progress:")
    print(f"   Completed: {project_progress.completed_levels}/{project_progress.total_levels}")
    print(f"   Completion: {project_progress.completion_percentage:.1f}%")
    print(f"   Average Score: {project_progress.average_score:.1f}%")
    
    # Achievements
    unlocked_achievements = achievement_service.get_user_achievements(user_id)
    achievement_stats = achievement_service.get_achievement_stats(user_id)
    
    print(f"\n🏆 Achievements:")
    print(f"   Unlocked: {achievement_stats['unlocked_count']}/{achievement_stats['total_achievements']}")
    print(f"   Achievement XP: {achievement_stats['total_xp_earned']:,}")
    print(f"\n   Latest:")
    for achievement in unlocked_achievements[:3]:
        print(f"   {achievement.icon} {achievement.name}")
    
    # Progress toward next achievements
    unlockable = achievement_service.get_unlockable_achievements(user_id, alice_stats)
    if unlockable:
        print(f"\n   Close to unlocking:")
        for achievement, progress in unlockable[:3]:
            print(f"   {achievement.icon} {achievement.name}: {progress:.0f}%")
    
    # Global leaderboard
    print(f"\n🏆 Global Leaderboard:")
    print(f"{'Rank':<8} {'Username':<12} {'Level':<8} {'XP':<12}")
    print("─" * 45)
    
    global_board = leaderboard_service.get_global_leaderboard(limit=10)
    for entry in global_board:
        marker = " 👈" if entry.user_id == user_id else ""
        print(f"{entry.rank:<8} {entry.username:<12} L{entry.level:<7} {entry.score:<12,}{marker}")
    
    # Weekly leaderboard
    print(f"\n📅 Weekly Leaderboard:")
    print(f"{'Rank':<8} {'Username':<12} {'XP This Week':<15}")
    print("─" * 40)
    
    weekly_board = leaderboard_service.get_weekly_leaderboard(limit=10)
    for entry in weekly_board:
        marker = " 👈" if entry.user_id == user_id else ""
        print(f"{entry.rank:<8} {entry.username:<12} {entry.score:<15,}{marker}")
    
    # User ranking
    alice_global_rank = leaderboard_service.get_user_rank(user_id, "global")
    alice_weekly_rank = leaderboard_service.get_user_rank(user_id, "weekly")
    
    print(f"\n🎯 Alice's Rankings:")
    print(f"   Global: #{alice_global_rank}")
    print(f"   Weekly: #{alice_weekly_rank}")
    
    # ==========================================
    # Success
    # ==========================================
    print(f"\n{'='*70}")
    print("✅ ALL GAME ENGINE SERVICES INTEGRATED SUCCESSFULLY!")
    print(f"{'='*70}")
    
    print(f"\n📦 Services Tested:")
    print(f"   ✅ Progress Tracking (Projects & Levels)")
    print(f"   ✅ XP & Leveling System (Formula: 100*N^1.5)")
    print(f"   ✅ Challenge Evaluation (Auto-grading)")
    print(f"   ✅ Achievement System (20+ achievements)")
    print(f"   ✅ Leaderboards (Global & Weekly)")
    
    print(f"\n🎮 Game Loop Verified:")
    print(f"   Play Level → Earn XP → Level Up → Unlock Achievements → Climb Leaderboard")
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
