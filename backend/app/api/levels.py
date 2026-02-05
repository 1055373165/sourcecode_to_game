"""
Level API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.level import Level, Challenge
from app.models.progress import UserProgress, ProgressStatus
from app.models.project import Project
from app.schemas.project import LevelDetailResponse, ChallengeResponse, LevelSubmission, LevelSubmissionResult, ChallengeResult
from app.core.exceptions import LevelNotFoundException

router = APIRouter()


@router.get("/{level_id}", response_model=LevelDetailResponse)
async def get_level(
    level_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get level details with all challenges
    
    - **level_id**: UUID of the level
    
    Returns level information with challenges (answers hidden)
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    
    if not level:
        raise LevelNotFoundException()
    
    # Get or create user progress for this level
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.level_id == level_id
    ).first()
    
    if not progress:
        # Initialize progress
        progress = UserProgress(
            user_id=current_user.id,
            level_id=level_id,
            status=ProgressStatus.NOT_STARTED
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
    
    # Mark as in progress if not started
    if progress.status == ProgressStatus.NOT_STARTED:
        progress.status = ProgressStatus.IN_PROGRESS
        progress.increment_attempt()
        db.commit()
    
    return LevelDetailResponse.model_validate(level)


@router.post("/{level_id}/submit", response_model=LevelSubmissionResult)
async def submit_level(
    level_id: str,
    submission: LevelSubmission,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit answers for a level
    
    - **level_id**: UUID of the level
    - **submission**: User's answers for all challenges
    
    Returns validation results and score
    """
    level = db.query(Level).filter(Level.id == level_id).first()
    
    if not level:
        raise LevelNotFoundException()
    
    # Get user progress
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.level_id == level_id
    ).first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level must be accessed before submitting"
        )
    
    # Validate answers and calculate score
    total_points = 0
    earned_points = 0
    challenge_results = []
    
    for challenge in level.challenges:
        total_points += challenge.points
        
        # Get user's answer for this challenge
        user_answer = submission.answers.get(challenge.id)
        
        if user_answer is None:
            # Challenge not answered
            challenge_results.append({
                "challenge_id": challenge.id,
                "is_correct": False,
                "points_earned": 0,
                "feedback": "No answer provided"
            })
            continue
        
        # Validate answer based on challenge type
        is_correct = validate_answer(challenge, user_answer)
        points = challenge.points if is_correct else 0
        earned_points += points
        
        challenge_results.append({
            "challenge_id": challenge.id,
            "is_correct": is_correct,
            "points_earned": points,
            "feedback": "Correct!" if is_correct else "Incorrect answer"
        })
    
    # Calculate percentage score
    score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    
    # Update progress
    progress.update_score(earned_points, total_points, submission.time_spent or 0)
    
    # Check if level is completed (e.g., 70% threshold)
    if score_percentage >= 70:
        progress.status = ProgressStatus.COMPLETED
        
        # Award XP to user if not already awarded for this level
        if progress.best_score < score_percentage:
            award_xp(current_user, level.xp_reward, db)
    
    db.commit()
    
    return LevelSubmissionResult(
        level_completed=score_percentage >= 70,
        score=earned_points,
        max_score=total_points,
        xp_earned=level.xp_reward if score_percentage >= 70 else 0,
        challenge_results=challenge_results
    )


def validate_answer(challenge: Challenge, user_answer: str) -> bool:
    """
    Validate user's answer against challenge correct answer
    
    Different challenge types may have different validation logic
    """
    import json
    
    # Get correct answer from challenge
    correct_answer = challenge.answer
    
    if challenge.type == "multiple_choice":
        # For multiple choice, answer is a single letter
        return user_answer.strip().upper() == correct_answer.get("correct_option", "").upper()
    
    elif challenge.type == "code_tracing":
        # For code tracing, answer might be a value
        return user_answer.strip() == str(correct_answer.get("expected_output", "")).strip()
    
    elif challenge.type == "fill_blank":
        # For fill in the blank, check if answer matches (case-insensitive)
        expected = correct_answer.get("correct_answer", "").strip().lower()
        return user_answer.strip().lower() == expected
    
    elif challenge.type == "code_completion":
        # For code completion, this would need more sophisticated checking
        # For MVP, do simple string matching
        expected = correct_answer.get("solution", "").strip()
        return user_answer.strip() == expected
    
    else:
        # Default: exact match
        return user_answer == str(correct_answer)


def award_xp(user: User, xp_amount: int, db: Session):
    """Award XP to user and check for level ups"""
    user.total_xp += xp_amount
    
    # Simple level calculation (every 1000 XP = 1 level)
    new_level = (user.total_xp // 1000) + 1
    
    if new_level > user.current_level:
        user.current_level = new_level
    
    db.commit()
