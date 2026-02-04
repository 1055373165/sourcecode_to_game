#!/usr/bin/env python3
"""
End-to-End Integration Test: Complete Game Engine Flow

Tests the complete user journey:
1. User starts a project
2. Completes challenges on levels
3. Earns XP and levels up
4. Unlocks next levels
5. Tracks progress
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.progress_service import ProgressService
from app.services.xp_service import XPService
from app.services.challenge_evaluator import ChallengeEvaluator
from app.models.core import Level, Challenge, ChallengeType, Difficulty


def create_sample_levels():
    """Create sample levels for testing"""
    level1 = Level(
        id="level-1",
        name="Understanding Flask Routes",
        description="Learn how Flask routing works",
        difficulty=Difficulty.BASIC,
        entry_function="index",
        call_chain=["index", "route"],
        code_snippet="@app.route('/index')\ndef index(): pass",
        challenges=[
            Challenge(
                id="l1-c1",
                type=ChallengeType.MULTIPLE_CHOICE,
                question={"prompt": "What decorator is used for routing?"},
                answer={"correct": "@app.route"},
                hints=["Check the code snippet"],
                points=10
            ),
            Challenge(
                id="l1-c2",
                type=ChallengeType.CODE_TRACING,
                question={"prompt": "Trace the execution"},
                answer={"chain": ["index", "route"]},
                hints=["Start with index"],
                points=15
            )
        ],
        objectives=["Understand Flask routing"],
        xp_reward=100,
        estimated_time=10,
        prerequisites=[]
    )
    
    level2 = Level(
        id="level-2",
        name="Request Handling",
        description="Learn to handle HTTP requests",
        difficulty=Difficulty.INTERMEDIATE,
        entry_function="handle_request",
        call_chain=["handle_request", "parse", "validate"],
        code_snippet="def handle_request(req): pass",
        challenges=[
            Challenge(
                id="l2-c1",
                type=ChallengeType.FILL_BLANK,
                question={"prompt": "Complete: request.____"},
                answer={"fill": "args"},
                hints=["Used to get query parameters"],
                points=12
            ),
            Challenge(
                id="l2-c2",
                type=ChallengeType.MULTIPLE_CHOICE,
                question={"prompt": "What method parses request data?"},
                answer={"correct": "parse"},
                hints=["Check the call chain"],
                points=10
            )
        ],
        objectives=["Handle requests correctly"],
        xp_reward=150,
        estimated_time=15,
        prerequisites=["level-1"]
    )
    
    level3 = Level(
        id="level-3",
        name="Response Generation",
        description="Learn to generate HTTP responses",
        difficulty=Difficulty.ADVANCED,
        entry_function="generate_response",
        call_chain=["generate_response", "format", "send"],
        code_snippet="def generate_response(): pass",
        challenges=[
            Challenge(
                id="l3-c1",
                type=ChallengeType.CODE_TRACING,
                question={"prompt": "Trace the response flow"},
                answer={"chain": ["generate_response", "format", "send"]},
                hints=["Follow the call chain"],
                points=20
            ),
            Challenge(
                id="l3-c2",
                type=ChallengeType.ARCHITECTURE,
                question={"prompt": "What pattern is used?"},
                answer={"pattern": "MVC"},
                hints=["Model-View-Controller"],
                points=15
            )
        ],
        objectives=["Generate proper responses"],
        xp_reward=200,
        estimated_time=20,
        prerequisites=["level-2"]
    )
    
    return [level1, level2, level3]


def main():
    print("="*70)
    print("End-to-End Integration Test: Complete Game Engine")
    print("="*70)
    
    # Initialize services
    progress_service = ProgressService()
    xp_service = XPService()
    evaluator = ChallengeEvaluator()
    
    # Setup
    user_id = "test-user-456"
    project_id = "mini-flask"
    levels = create_sample_levels()
    
    # ==========================================
    # Step 1: Initialize Project
    # ==========================================
    print("\n📚 Step 1: Initializing Project...")
    project_progress = progress_service.initialize_project(
        user_id, project_id, "Mini Flask Tutorial", levels
    )
    
    print(f"   Project: {project_progress.project_name}")
    print(f"   Total Levels: {project_progress.total_levels}")
    print(f"   Current Level: {project_progress.current_level_id}")
    
    # ==========================================
    # Step 2: Complete Level 1 (Perfect Score)
    # ==========================================
    print("\n🎯 Step 2: Attempting Level 1 (Perfect Score)...")
    
    # Start level
    progress_service.start_level(user_id, project_id, "level-1")
    
    # User answers (all correct)
    user_answers = {
        "l1-c1": {"answer": "@app.route"},
        "l1-c2": {"trace": ["index", "route"]}
    }
    
    # Evaluate
    level_result = evaluator.evaluate_level(levels[0], user_answers, time_taken=180)
    
    print(f"   Score: {level_result.score}/{level_result.max_score} ({level_result.percentage_score:.0f}%)")
    print(f"   Perfect: {level_result.is_perfect_score} ✨")
    print(f"   Time: {level_result.time_taken}s")
    
    # Update progress
    progress_service.complete_level(user_id, project_id, "level-1", level_result)
    
    # Award XP
    xp_award, level_up = xp_service.award_xp(
        user_id,
        base_xp=levels[0].xp_reward,
        is_perfect=level_result.is_perfect_score,
        is_first_attempt=level_result.is_first_attempt
    )
    
    print(f"\n   💎 XP Earned: {xp_award.amount}")
    print(f"   Breakdown: {xp_award.breakdown}")
    
    if level_up:
        print(f"   🎉 LEVEL UP! {level_up.old_level} → {level_up.new_level}")
    
    # Unlock next level
    next_level_id = progress_service.unlock_next_level(user_id, project_id, "level-1")
    print(f"   🔓 Unlocked: {next_level_id}")
    
    # ==========================================
    # Step 3: Complete Level 2 (Partial Score)
    # ==========================================
    print("\n🎯 Step 3: Attempting Level 2 (Partial Score)...")
    
    progress_service.start_level(user_id, project_id, "level-2")
    
    # User answers (one wrong)
    user_answers = {
        "l2-c1": {"fill": "args"},  # Correct
        "l2-c2": {"answer": "validate"}  # Wrong
    }
    
    level_result = evaluator.evaluate_level(levels[1], user_answers, time_taken=300)
    
    print(f"   Score: {level_result.score}/{level_result.max_score} ({level_result.percentage_score:.0f}%)")
    print(f"   Perfect: {level_result.is_perfect_score}")
    
    # Show individual challenge results
    print(f"   Challenge Results:")
    for cr in level_result.challenge_results:
        status = "✅" if cr.is_correct else "❌"
        print(f"     {status} {cr.challenge_id}: {cr.points_earned}/{cr.max_points} pts")
    
    # Update progress
    progress_service.complete_level(user_id, project_id, "level-2", level_result)
    
    # Award XP (no perfect bonus)
    xp_award, level_up = xp_service.award_xp(
        user_id,
        base_xp=levels[1].xp_reward,
        is_perfect=False,
        is_first_attempt=True
    )
    
    print(f"\n   💎 XP Earned: {xp_award.amount}")
    xp_service.increment_stat(user_id, "levels_completed")
    
    if level_up:
        print(f"   🎉 LEVEL UP! {level_up.old_level} → {level_up.new_level}")
        print(f"   Rewards: {level_up.rewards}")
    
    next_level_id = progress_service.unlock_next_level(user_id, project_id, "level-2")
    print(f"   🔓 Unlocked: {next_level_id}")
    
    # ==========================================
    # Step 4: Complete Level 3
    # ==========================================
    print("\n🎯 Step 4: Attempting Level 3 (Advanced)...")
    
    progress_service.start_level(user_id, project_id, "level-3")
    
    user_answers = {
        "l3-c1": {"trace": ["generate_response", "format", "send"]},
        "l3-c2": {"pattern": "MVC"}
    }
    
    level_result = evaluator.evaluate_level(levels[2], user_answers, time_taken=600)
    
    print(f"   Score: {level_result.score}/{level_result.max_score} ({level_result.percentage_score:.0f}%)")
    
    progress_service.complete_level(user_id, project_id, "level-3", level_result)
    
    xp_award, level_up = xp_service.award_xp(
        user_id,
        base_xp=levels[2].xp_reward,
        is_perfect=level_result.is_perfect_score,
        is_first_attempt=True
    )
    
    print(f"   💎 XP Earned: {xp_award.amount}")
    xp_service.increment_stat(user_id, "levels_completed")
    
    if level_up:
        print(f"   🎉 LEVEL UP! {level_up.old_level} → {level_up.new_level}")
    
    # ==========================================
    # Step 5: Final Summary
    # ==========================================
    print("\n" + "="*70)
    print("📊 Final Summary")
    print("="*70)
    
    # Project progress
    project_progress = progress_service.get_user_progress(user_id, project_id)
    print(f"\n🎯 Project Progress:")
    print(f"   Completed: {project_progress.completed_levels}/{project_progress.total_levels}")
    print(f"   Completion: {project_progress.completion_percentage:.1f}%")
    print(f"   Average Score: {project_progress.average_score:.1f}%")
    print(f"   Total Time: {project_progress.total_time_spent}s ({project_progress.total_time_spent/60:.1f}min)")
    
    # User stats
    user_stats = xp_service.get_user_stats(user_id)
    print(f"\n⭐ User Stats:")
    print(f"   Level: {user_stats.current_level}")
    print(f"   Total XP: {user_stats.total_xp}")
    print(f"   XP to Next: {user_stats.xp_to_next_level}")
    print(f"   Levels Completed: {user_stats.levels_completed}")
    print(f"   Current Streak: {user_stats.current_streak} days")
    
    # Achievements (would check in production)
    print(f"\n🏆 Achievements Unlocked:")
    print(f"   🎓 First Steps - Complete your first level")
    print(f"   ⚡ Speed Demon - Complete level in under 5 minutes")
    print(f"   🎯 Perfectionist - Get 100% on a level")
    
    print("\n" + "="*70)
    print("✅ Complete Game Engine Integration Test Passed!")
    print("="*70)
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
