"""
Challenge Evaluator

Automatic grading system for different challenge types.
Provides immediate feedback and partial credit where appropriate.
"""

from typing import Dict, List, Any, Optional
import re

from app.models.core import Challenge, ChallengeType, Level
from app.services.models import ChallengeResult, LevelResult


class ChallengeEvaluator:
    """
    Evaluates user answers for different challenge types
    
    Supported types:
    - Multiple Choice
    - Code Tracing
    - Fill in the Blank
    - Code Completion (basic validation)
    - Debugging (pattern matching)
    - Architecture (multiple choice variant)
    """
    
    def evaluate_challenge(
        self,
        challenge: Challenge,
        user_answer: Dict[str, Any]
    ) -> ChallengeResult:
        """
        Evaluate a single challenge
        
        Args:
            challenge: Challenge definition
            user_answer: User's answer (format depends on challenge type)
        
        Returns:
            ChallengeResult with score and feedback
        """
        if challenge.type == ChallengeType.MULTIPLE_CHOICE:
            return self._evaluate_multiple_choice(challenge, user_answer)
        elif challenge.type == ChallengeType.CODE_TRACING:
            return self._evaluate_code_tracing(challenge, user_answer)
        elif challenge.type == ChallengeType.FILL_BLANK:
            return self._evaluate_fill_blank(challenge, user_answer)
        elif challenge.type == ChallengeType.CODE_COMPLETION:
            return self._evaluate_code_completion(challenge, user_answer)
        elif challenge.type == ChallengeType.DEBUGGING:
            return self._evaluate_debugging(challenge, user_answer)
        elif challenge.type == ChallengeType.ARCHITECTURE:
            return self._evaluate_architecture(challenge, user_answer)
        else:
            return ChallengeResult(
                challenge_id=challenge.id,
                is_correct=False,
                points_earned=0,
                max_points=challenge.points,
                feedback="Unknown challenge type"
            )
    
    def _evaluate_multiple_choice(
        self,
        challenge: Challenge,
        user_answer: Dict[str, Any]
    ) -> ChallengeResult:
        """
        Evaluate multiple choice question
        
        Expected user_answer format: {"answer": "selected_option"}
        Expected challenge.answer format: {"correct": "correct_option"}
        """
        user_selection = user_answer.get("answer", "").strip()
        correct_answer = challenge.answer.get("correct", "").strip()
        
        is_correct = user_selection.lower() == correct_answer.lower()
        
        if is_correct:
            feedback = "✅ Correct!"
            points = challenge.points
        else:
            feedback = f"❌ Incorrect. The correct answer is: {correct_answer}"
            points = 0
        
        return ChallengeResult(
            challenge_id=challenge.id,
            is_correct=is_correct,
            points_earned=points,
            max_points=challenge.points,
            feedback=feedback,
            hints=challenge.hints if not is_correct else []
        )
    
    def _evaluate_code_tracing(
        self,
        challenge: Challenge,
        user_answer: Dict[str, Any]
    ) -> ChallengeResult:
        """
        Evaluate code tracing question with partial credit
        
        Expected user_answer format: {"trace": ["func1", "func2", ...]}
        Expected challenge.answer format: {"chain": ["func1", "func2", ...]}
        """
        user_trace = user_answer.get("trace", [])
        correct_chain = challenge.answer.get("chain", [])
        
        if not correct_chain:
            return ChallengeResult(
                challenge_id=challenge.id,
                is_correct=False,
                points_earned=0,
                max_points=challenge.points,
                feedback="No correct answer defined"
            )
        
        # Calculate how many functions are correct in sequence
        correct_count = 0
        for i, func in enumerate(user_trace):
            if i < len(correct_chain) and func == correct_chain[i]:
                correct_count += 1
            else:
                break  # Stop at first mismatch
        
        # Award partial credit
        percentage = correct_count / len(correct_chain) if correct_chain else 0
        points = int(challenge.points * percentage)
        is_correct = correct_count == len(correct_chain)
        
        if is_correct:
            feedback = f"✅ Perfect trace! Complete execution flow: {' → '.join(correct_chain)}"
        elif correct_count > 0:
            feedback = f"⚠️ Partially correct ({correct_count}/{len(correct_chain)} steps). "
            feedback += f"You got up to: {' → '.join(user_trace[:correct_count])}"
        else:
            feedback = f"❌ Incorrect. The execution flow is: {' → '.join(correct_chain)}"
        
        return ChallengeResult(
            challenge_id=challenge.id,
            is_correct=is_correct,
            points_earned=points,
            max_points=challenge.points,
            feedback=feedback,
            hints=challenge.hints if not is_correct else []
        )
    
    def _evaluate_fill_blank(
        self,
        challenge: Challenge,
        user_answer: Dict[str, Any]
    ) -> ChallengeResult:
        """
        Evaluate fill-in-the-blank with partial credit
        
        Expected user_answer format: {"fills": {"blank1": "answer1", "blank2": "answer2"}}
        Expected challenge.answer format: {"fill": "answer"} or {"fills": {"blank1": "ans1", ...}}
        """
        # Handle single fill
        if "fill" in user_answer:
            user_fill = user_answer["fill"].strip()
            correct_fill = challenge.answer.get("fill", "").strip()
            
            # Flexible matching (case-insensitive, whitespace-agnostic)
            is_correct = self._flexible_match(user_fill, correct_fill)
            
            if is_correct:
                feedback = "✅ Correct!"
                points = challenge.points
            else:
                feedback = f"❌ Incorrect. The answer is: {correct_fill}"
                points = 0
        
        # Handle multiple fills
        else:
            user_fills = user_answer.get("fills", {})
            correct_fills = challenge.answer.get("fills", {})
            
            if not correct_fills:
                return ChallengeResult(
                    challenge_id=challenge.id,
                    is_correct=False,
                    points_earned=0,
                    max_points=challenge.points,
                    feedback="No correct answer defined"
                )
            
            # Count correct fills
            correct_count = 0
            for key, correct_value in correct_fills.items():
                user_value = user_fills.get(key, "")
                if self._flexible_match(user_value, correct_value):
                    correct_count += 1
            
            # Award partial credit
            percentage = correct_count / len(correct_fills)
            points = int(challenge.points * percentage)
            is_correct = correct_count == len(correct_fills)
            
            if is_correct:
                feedback = f"✅ All {len(correct_fills)} blanks filled correctly!"
            else:
                feedback = f"⚠️ {correct_count}/{len(correct_fills)} blanks correct."
        
        return ChallengeResult(
            challenge_id=challenge.id,
            is_correct=is_correct,
            points_earned=points,
            max_points=challenge.points,
            feedback=feedback,
            hints=challenge.hints if not is_correct else []
        )
    
    def _evaluate_code_completion(
        self,
        challenge: Challenge,
        user_answer: Dict[str, Any]
    ) -> ChallengeResult:
        """
        Evaluate code completion (basic pattern matching)
        
        In production, this would run actual code tests.
        For now, we use pattern matching.
        
        Expected user_answer format: {"code": "user's code"}
        Expected challenge.answer format: {"patterns": ["pattern1", ...]} or {"code": "expected"}
        """
        user_code = user_answer.get("code", "").strip()
        
        # Check for required patterns
        if "patterns" in challenge.answer:
            patterns = challenge.answer["patterns"]
            matches = sum(1 for pattern in patterns if pattern in user_code)
            
            percentage = matches / len(patterns) if patterns else 0
            points = int(challenge.points * percentage)
            is_correct = matches == len(patterns)
            
            if is_correct:
                feedback = "✅ Code looks good! All required patterns present."
            else:
                feedback = f"⚠️ Missing some required patterns ({matches}/{len(patterns)} found)."
        
        # Check for exact match (simplified)
        elif "code" in challenge.answer:
            expected_code = challenge.answer["code"].strip()
            is_correct = self._normalize_code(user_code) == self._normalize_code(expected_code)
            
            if is_correct:
                feedback = "✅ Perfect code!"
                points = challenge.points
            else:
                feedback = "❌ Code doesn't match expected solution."
                points = 0
        
        else:
            # No validation criteria
            feedback = "Code submitted (auto-graded)"
            points = challenge.points
            is_correct = True
        
        return ChallengeResult(
            challenge_id=challenge.id,
            is_correct=is_correct,
            points_earned=points,
            max_points=challenge.points,
            feedback=feedback,
            hints=challenge.hints if not is_correct else []
        )
    
    def _evaluate_debugging(
        self,
        challenge: Challenge,
        user_answer: Dict[str, Any]
    ) -> ChallengeResult:
        """
        Evaluate debugging challenge
        
        Expected user_answer format: {"fixed_code": "corrected code"}
        Expected challenge.answer format: {"patterns": [...]} or {"fixed_code": "..."}
        """
        # Similar to code completion
        return self._evaluate_code_completion(challenge, {"code": user_answer.get("fixed_code", "")})
    
    def _evaluate_architecture(
        self,
        challenge: Challenge,
        user_answer: Dict[str, Any]
    ) -> ChallengeResult:
        """
        Evaluate architecture question (like multiple choice)
        
        Expected user_answer format: {"pattern": "selected_pattern"}
        Expected challenge.answer format: {"pattern": "correct_pattern"}
        """
        user_selection = user_answer.get("pattern", "").strip()
        correct_pattern = challenge.answer.get("pattern", "").strip()
        
        is_correct = user_selection.lower() == correct_pattern.lower()
        
        if is_correct:
            feedback = f"✅ Correct! This is the {correct_pattern} pattern."
            points = challenge.points
        else:
            feedback = f"❌ Incorrect. The pattern used is: {correct_pattern}"
            points = 0
        
        return ChallengeResult(
            challenge_id=challenge.id,
            is_correct=is_correct,
            points_earned=points,
            max_points=challenge.points,
            feedback=feedback,
            hints=challenge.hints if not is_correct else []
        )
    
    def evaluate_level(
        self,
        level: Level,
        user_answers: Dict[str, Dict[str, Any]],
        time_taken: int = 0,
        hints_used: int = 0
    ) -> LevelResult:
        """
        Evaluate all challenges in a level
        
        Args:
            level: Level definition
            user_answers: Dict mapping challenge_id to user's answer
            time_taken: Time spent on level (seconds)
            hints_used: Number of hints used
        
        Returns:
            LevelResult with overall score and challenge results
        """
        challenge_results: List[ChallengeResult] = []
        total_score = 0
        max_score = 0
        
        # Get attempts (for first attempt bonus)
        # This would come from ProgressService in real implementation
        is_first_attempt = True  # Simplified
        
        # Evaluate each challenge
        for challenge in level.challenges:
            user_answer = user_answers.get(challenge.id, {})
            result = self.evaluate_challenge(challenge, user_answer)
            
            challenge_results.append(result)
            total_score += result.points_earned
            max_score += result.max_points
        
        # Determine if level is completed (70% threshold)
        completion_threshold = 0.7
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        level_completed = percentage >= (completion_threshold * 100)
        
        is_perfect = total_score == max_score
        
        return LevelResult(
            level_id=level.id,
            level_completed=level_completed,
            score=total_score,
            max_score=max_score,
            challenge_results=challenge_results,
            time_taken=time_taken,
            hints_used=hints_used,
            is_first_attempt=is_first_attempt,
            is_perfect_score=is_perfect
        )
    
    def _flexible_match(self, user_input: str, correct_answer: str) -> bool:
        """
        Flexible string matching (case-insensitive, whitespace-agnostic)
        
        Args:
            user_input: User's answer
            correct_answer: Expected answer
        
        Returns:
            True if match, False otherwise
        """
        # Normalize both strings
        user_normalized = re.sub(r'\s+', '', user_input.lower())
        correct_normalized = re.sub(r'\s+', '', correct_answer.lower())
        
        return user_normalized == correct_normalized
    
    def _normalize_code(self, code: str) -> str:
        """
        Normalize code for comparison
        
        Args:
            code: Source code
        
        Returns:
            Normalized code
        """
        # Remove comments
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code)
        
        return code.strip().lower()


# ============================================
# Example Usage & Demo
# ============================================

if __name__ == '__main__':
    from app.models.core import Difficulty
    
    print("="*60)
    print("Challenge Evaluator Demo")
    print("="*60)
    
    evaluator = ChallengeEvaluator()
    
    # Test Multiple Choice
    print("\n1. Multiple Choice Challenge...")
    mc_challenge = Challenge(
        id="mc1",
        type=ChallengeType.MULTIPLE_CHOICE,
        question={"prompt": "What is WSGI?", "options": ["A", "B", "C", "D"]},
        answer={"correct": "Web Server Gateway Interface"},
        hints=["It's a Python standard"],
        points=10
    )
    
    result = evaluator.evaluate_challenge(mc_challenge, {"answer": "Web Server Gateway Interface"})
    print(f"   User answered: Web Server Gateway Interface")
    print(f"   Result: {result.feedback}")
    print(f"   Points: {result.points_earned}/{result.max_points}")
    
    # Test Code Tracing with partial credit
    print("\n2. Code Tracing Challenge (Partial Credit)...")
    trace_challenge = Challenge(
        id="trace1",
        type=ChallengeType.CODE_TRACING,
        question={"prompt": "Trace execution"},
        answer={"chain": ["index", "route", "Response", "send"]},
        hints=["Start with index"],
        points=15
    )
    
    result = evaluator.evaluate_challenge(trace_challenge, {"trace": ["index", "route", "Response"]})
    print(f"   User trace: index → route → Response")
    print(f"   Correct trace: index → route → Response → send")
    print(f"   Result: {result.feedback}")
    print(f"   Points: {result.points_earned}/{result.max_points} (Partial credit!)")
    
    # Test Fill Blank
    print("\n3. Fill in the Blank Challenge...")
    fill_challenge = Challenge(
        id="fill1",
        type=ChallengeType.FILL_BLANK,
        question={"prompt": "Complete: @app.____('/index')"},
        answer={"fill": "route"},
        hints=["Used for URL mapping"],
        points=12
    )
    
    result = evaluator.evaluate_challenge(fill_challenge, {"fill": "route"})
    print(f"   User filled: route")
    print(f"   Result: {result.feedback}")
    print(f"   Points: {result.points_earned}/{result.max_points}")
    
    # Test Level Evaluation
    print("\n4. Complete Level Evaluation...")
    level = Level(
        id="level-1",
        name="Understanding Flask",
        description="Learn Flask basics",
        difficulty=Difficulty.BASIC,
        entry_function="index",
        call_chain=["index", "route"],
        code_snippet="# Flask code",
        challenges=[mc_challenge, trace_challenge, fill_challenge],
        objectives=["Learn routing"],
        xp_reward=100,
        estimated_time=10,
        prerequisites=[]
    )
    
    user_answers = {
        "mc1": {"answer": "Web Server Gateway Interface"},
        "trace1": {"trace": ["index", "route", "Response", "send"]},
        "fill1": {"fill": "route"}
    }
    
    level_result = evaluator.evaluate_level(level, user_answers, time_taken=420)
    
    print(f"   Level: {level.name}")
    print(f"   Completed: {level_result.level_completed}")
    print(f"   Score: {level_result.score}/{level_result.max_score} ({level_result.percentage_score:.1f}%)")
    print(f"   Perfect Score: {level_result.is_perfect_score}")
    print(f"   Time: {level_result.time_taken}s")
    print(f"\n   Challenge Results:")
    for cr in level_result.challenge_results:
        status = "✅" if cr.is_correct else "⚠️"
        print(f"     {status} {cr.challenge_id}: {cr.points_earned}/{cr.max_points} pts")
    
    print("\n" + "="*60)
    print("✓ Challenge Evaluator is working!")
    print("="*60)
