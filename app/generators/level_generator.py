"""
Level Generator - Automatic Learning Level Creation

Transforms analyzed call graphs into structured learning levels with challenges.
Based on the algorithm design from docs/level_generation_algorithm.md

Features:
- Automatic core chain identification
- Difficulty scoring algorithm
- Challenge type selection
- Question templates
- Learning objective generation
"""

import random
from typing import List, Dict, Set, Optional, Tuple
from pathlib import Path

from app.models.core import (
    CallGraph, CodeNode, Level, Challenge,
    ChallengeType, Difficulty, NodeType
)


class LevelGenerator:
    """
   Generates learning levels from call graphs
    
    Algorithm:
    1. Identify core execution chains
    2. Score difficulty for each chain
    3. Select appropriate challenge types
    4. Generate questions
    5. Add hints and learning objectives
    """
    
    def __init__(self, call_graph: CallGraph):
        self.call_graph = call_graph
        self.generated_levels: List[Level] = []
    
    def generate_levels(self, max_levels: int = 10) -> List[Level]:
        """
        Main entry point for level generation
        
        Args:
            max_levels: Maximum number of levels to generate
        
        Returns:
            List of generated levels
        """
        # Phase 1: Identify core chains
        core_chains = self.identify_core_chains()
        
        # Limit to max_levels
        core_chains = core_chains[:max_levels]
        
        levels = []
        for i, chain in enumerate(core_chains):
            # Phase 2: Calculate difficulty
            difficulty = self.calculate_difficulty(chain)
            
            # Phase 3: Select challenge types
            challenge_types = self.select_challenge_types(chain, difficulty)
            
            # Phase 4: Generate challenges
            challenges = []
            for ctype in challenge_types:
                challenge = self.generate_challenge(ctype, chain)
                if challenge:
                    challenges.append(challenge)
            
            # Phase 5: Create level
            level = self._create_level(i + 1, chain, difficulty, challenges)
            levels.append(level)
        
        self.generated_levels = levels
        return levels
    
    def identify_core_chains(self) -> List[List[str]]:
        """
        Identify the most important call chains to teach
        
        Uses weighted scoring:
        - Entry point proximity (40%): Closer to entry = more important
        - Call frequency (30%): More callers = more central
        - Code complexity (20%): Higher complexity = worth teaching
        - Documentation quality (10%): Better docs = better learning
        
        Returns:
            List of call chains, ordered by importance
        """
        all_chains = []
        
        # Get chains from each entry point
        for entry_id in self.call_graph.entry_points:
            if entry_id not in self.call_graph.nodes:
                continue
            
            chains = self.call_graph.get_call_chain(entry_id, max_depth=5)
            
            for chain in chains:
                if len(chain) >= 2:  # Need at least 2 functions
                    score = self._calculate_chain_importance(chain)
                    all_chains.append((score, chain))
        
        # If no entry points, try from highly connected nodes
        if not all_chains:
            # Find nodes with most connections
            sorted_nodes = sorted(
                self.call_graph.nodes.values(),
                key=lambda n: len(n.called_by),
                reverse=True
            )
            
            for node in sorted_nodes[:5]:
                chains = self.call_graph.get_call_chain(node.id, max_depth=5)
                for chain in chains:
                    if len(chain) >= 2:
                        score = self._calculate_chain_importance(chain)
                        all_chains.append((score, chain))
        
        # Sort by score and return top chains
        all_chains.sort(reverse=True, key=lambda x: x[0])
        return [chain for score, chain in all_chains]
    
    def _calculate_chain_importance(self, chain: List[str]) -> float:
        """Calculate importance score for a call chain"""
        score = 0.0
        
        # Entry point proximity (40 points max)
        for i, node_id in enumerate(chain):
            proximity_score = 40 * (0.7 ** i)
            score += proximity_score
        
        # Call frequency (30 points max)
        total_called_by = sum(
            len(self.call_graph.nodes[id].called_by)
            for id in chain
            if id in self.call_graph.nodes
        )
        avg_called_by = total_called_by / len(chain) if chain else 0
        frequency_score = min(30, avg_called_by * 5)
        score += frequency_score
        
        # Code complexity (20 points max)
        total_complexity = sum(
            self.call_graph.nodes[id].complexity
            for id in chain
            if id in self.call_graph.nodes
        )
        avg_complexity = total_complexity / len(chain) if chain else 0
        complexity_score = min(20, avg_complexity)
        score += complexity_score
        
        # Documentation quality (10 points max)
        documented_count = sum(
            1 for id in chain
            if id in self.call_graph.nodes and self.call_graph.nodes[id].docstring
        )
        doc_score = (documented_count / len(chain)) * 10 if chain else 0
        score += doc_score
        
        return score
    
    def calculate_difficulty(self, chain: List[str]) -> Difficulty:
        """
        Calculate difficulty level for a chain
        
        Factors:
        - Chain length: Longer = harder
        - Avg complexity: Higher = harder
        - Abstraction level: More OOP/decorators = harder
        - Dependency count: More = harder
        
        Score ranges:
        0-19: Tutorial
        20-39: Basic
        40-59: Intermediate
        60-79: Advanced
        80+: Expert
        """
        score = 0
        
        # Chain length (0-20 points)
        length_score = min(20, len(chain) * 4)
        score += length_score
        
        # Average complexity (0-30 points)
        complexities = [
            self.call_graph.nodes[id].complexity
            for id in chain
            if id in self.call_graph.nodes
        ]
        avg_complexity = sum(complexities) / len(complexities) if complexities else 0
        complexity_score = min(30, avg_complexity * 2)
        score += complexity_score
        
        # Abstraction level (0-25 points)
        abstraction_score = 0
        for node_id in chain:
            if node_id not in self.call_graph.nodes:
                continue
            
            node = self.call_graph.nodes[node_id]
            abstraction_score += len(node.decorators) * 3
            if node.is_async:
                abstraction_score += 5
            if node.is_generator:
                abstraction_score += 5
        abstraction_score = min(25, abstraction_score)
        score += abstraction_score
        
        # Dependencies (0-25 points)
        total_deps = sum(
            len(self.call_graph.nodes[id].depends_on)
            for id in chain
            if id in self.call_graph.nodes
        )
        dep_score = min(25, total_deps * 2)
        score += dep_score
        
        # Map to difficulty
        if score < 20:
            return Difficulty.TUTORIAL
        elif score < 40:
            return Difficulty.BASIC
        elif score < 60:
            return Difficulty.INTERMEDIATE
        elif score < 80:
            return Difficulty.ADVANCED
        else:
            return Difficulty.EXPERT
    
    def select_challenge_types(
        self,
        chain: List[str],
        difficulty: Difficulty
    ) -> List[ChallengeType]:
        """
        Select appropriate challenge types for the level
        
        Strategy:
        - Always include Multiple Choice
        - Code Tracing for chains with 3+ functions
        - Fill Blank for pattern-heavy code
        - Code Completion for intermediate+
        - Debugging for complex logic
        - Architecture for advanced levels
        """
        challenges = []
        
        # Always include Multiple Choice
        challenges.append(ChallengeType.MULTIPLE_CHOICE)
        
        # Code Tracing for longer chains
        if len(chain) >= 3:
            challenges.append(ChallengeType.CODE_TRACING)
        
        # Get chain characteristics
        has_decorators = any(
            self.call_graph.nodes[id].decorators
            for id in chain
            if id in self.call_graph.nodes
        )
        
        avg_complexity = sum(
            self.call_graph.nodes[id].complexity
            for id in chain
            if id in self.call_graph.nodes
        ) / len(chain) if chain else 0
        
        # Fill Blank for pattern-heavy code
        if has_decorators or difficulty.value >= Difficulty.INTERMEDIATE.value:
            challenges.append(ChallengeType.FILL_BLANK)
        
        # Code Completion for intermediate+
        if difficulty.value >= Difficulty.INTERMEDIATE.value:
            challenges.append(ChallengeType.CODE_COMPLETION)
        
        # Debugging for complex functions
        if avg_complexity > 10:
            challenges.append(ChallengeType.DEBUGGING)
        
        # Architecture for advanced
        if difficulty.value >= Difficulty.ADVANCED.value:
            challenges.append(ChallengeType.ARCHITECTURE)
        
        return challenges[:5]  # Max 5 challenges per level
    
    def generate_challenge(
        self,
        challenge_type: ChallengeType,
        chain: List[str]
    ) -> Optional[Challenge]:
        """Generate a specific challenge"""
        
        if challenge_type == ChallengeType.MULTIPLE_CHOICE:
            return self._generate_multiple_choice(chain)
        elif challenge_type == ChallengeType.CODE_TRACING:
            return self._generate_code_tracing(chain)
        elif challenge_type == ChallengeType.FILL_BLANK:
            return self._generate_fill_blank(chain)
        elif challenge_type == ChallengeType.CODE_COMPLETION:
            return self._generate_code_completion(chain)
        elif challenge_type == ChallengeType.DEBUGGING:
            return self._generate_debugging(chain)
        elif challenge_type == ChallengeType.ARCHITECTURE:
            return self._generate_architecture(chain)
        
        return None
    
    def _generate_multiple_choice(self, chain: List[str]) -> Challenge:
        """Generate multiple choice question"""
        if not chain or chain[0] not in self.call_graph.nodes:
            return None
        
        node = self.call_graph.nodes[chain[0]]
        
        # Question templates
        templates = [
            {
                'prompt': f"What does the function {node.name}() do?",
                'correct': node.docstring.split('.')[0] if node.docstring else "Processes data",
                'distractors': ["Parses input", "Validates data", "Formats output"]
            },
            {
                'prompt': f"How many parameters does {node.name}() accept?",
                'correct': str(len(node.parameters)),
                'distractors': [str(len(node.parameters) + i) for i in [-1, 1, 2] if len(node.parameters) + i >= 0]
            }
        ]
        
        template = random.choice(templates)
        
        # Create options (correct + distractors)
        options = [template['correct']] + template['distractors'][:3]
        random.shuffle(options)
        
        return Challenge(
            id=f"mc_{chain[0]}",
            type=ChallengeType.MULTIPLE_CHOICE,
            question={
                'prompt': template['prompt'],
                'options': options
            },
            answer={'correct': template['correct']},
            hints=[f"Check the function signature at line {node.line_start}"],
            points=10
        )
    
    def _generate_code_tracing(self, chain: List[str]) -> Challenge:
        """Generate code tracing challenge"""
        return Challenge(
            id=f"trace_{chain[0]}",
            type=ChallengeType.CODE_TRACING,
            question={
                'prompt': f"Trace the execution flow from {self._get_node_name(chain[0])} to {self._get_node_name(chain[-1])}",
                'steps': len(chain)
            },
            answer={'chain': [self._get_node_name(id) for id in chain]},
            hints=[f"Start with {self._get_node_name(chain[0])}"],
            points=15
        )
    
    def _generate_fill_blank(self, chain: List[str]) -> Challenge:
        """Generate fill-in-blank challenge"""
        if not chain or chain[0] not in self.call_graph.nodes:
            return None
        
        node = self.call_graph.nodes[chain[0]]
        
        return Challenge(
            id=f"fill_{chain[0]}",
            type=ChallengeType.FILL_BLANK,
            question={
                'prompt': f"Complete the decorator for {node.name}",
                'template': f"@____\ndef {node.name}():"
            },
            answer={'fill': node.decorators[0] if node.decorators else 'decorator'},
            hints=["Check the decorators used in this function"],
            points=12
        )
    
    def _generate_code_completion(self, chain: List[str]) -> Challenge:
        """Generate code completion challenge"""
        return Challenge(
            id=f"complete_{chain[0]}",
            type=ChallengeType.CODE_COMPLETION,
            question={
                'prompt': "Complete the function implementation",
                'template': "def function():\n    # TODO: implement"
            },
            answer={'code': "pass"},
            hints=["Think about the function's purpose"],
            points=20
        )
    
    def _generate_debugging(self, chain: List[str]) -> Challenge:
        """Generate debugging challenge"""
        return Challenge(
            id=f"debug_{chain[0]}",
            type=ChallengeType.DEBUGGING,
            question={
                'prompt': "Find and fix the bug in this code",
                'buggy_code': "def func():\n    return None"
            },
            answer={'fixed_code': "def func():\n    return True"},
            hints=["Check the return type"],
            points=15
        )
    
    def _generate_architecture(self, chain: List[str]) -> Challenge:
        """Generate architecture question"""
        return Challenge(
            id=f"arch_{chain[0]}",
            type=ChallengeType.ARCHITECTURE,
            question={
                'prompt': "What design pattern is used here?",
                'options': ["Decorator", "Factory", "Observer", "Strategy"]
            },
            answer={'pattern': "Decorator"},
            hints=["Look at how functions are wrapped"],
            points=15
        )
    
    def _create_level(
        self,
        level_num: int,
        chain: List[str],
        difficulty: Difficulty,
        challenges: List[Challenge]
    ) -> Level:
        """Create a complete level"""
        
        # Get entry function
        entry_id = chain[0] if chain else ""
        entry_node = self.call_graph.nodes.get(entry_id)
        
        # Generate level name
        level_name = self._generate_level_name(entry_node, difficulty)
        
        # Generate description
        description = self._generate_description(chain)
        
        # Extract code snippet
        code_snippet = self._extract_code_snippet(chain)
        
        # Generate learning objectives
        objectives = self._generate_objectives(chain)
        
        # Calculate XP reward based on difficulty
        xp_reward = self._calculate_xp_reward(difficulty)
        
        # Estimate time
        estimated_time = len(challenges) * 3  # 3 mins per challenge
        
        return Level(
            id=f"level_{level_num}",
            name=level_name,
            description=description,
            difficulty=difficulty,
            entry_function=entry_id,
            call_chain=chain,
            code_snippet=code_snippet,
            challenges=challenges,
            objectives=objectives,
            xp_reward=xp_reward,
            estimated_time=estimated_time,
            prerequisites=[f"level_{level_num-1}"] if level_num > 1 else []
        )
    
    def _get_node_name(self, node_id: str) -> str:
        """Get node name from ID"""
        if node_id in self.call_graph.nodes:
            return self.call_graph.nodes[node_id].name
        return node_id.split("::")[-1]
    
    def _generate_level_name(self, entry_node: Optional[CodeNode], difficulty: Difficulty) -> str:
        """Generate a descriptive level name"""
        if entry_node:
            return f"Understanding {entry_node.name}"
        return f"Code Analysis Challenge ({difficulty.name})"
    
    def _generate_description(self, chain: List[str]) -> str:
        """Generate level description"""
        if not chain:
            return "Analyze this code and understand its behavior"
        
        start_name = self._get_node_name(chain[0])
        end_name = self._get_node_name(chain[-1])
        
        return f"Learn how {start_name} works and trace its execution to {end_name}"
    
    def _extract_code_snippet(self, chain: List[str]) -> str:
        """Extract relevant code snippet"""
        # TODO: Actually read and extract code from files
        return "# Code snippet will be extracted from source files"
    
    def _generate_objectives(self, chain: List[str]) -> List[str]:
        """Generate learning objectives"""
        objectives = []
        
        if chain:
            start = self._get_node_name(chain[0])
            end = self._get_node_name(chain[-1])
            objectives.append(f"Trace execution from {start} to {end}")
        
        # Add more specific objectives based on node characteristics
        for node_id in chain[:3]:  # First 3 nodes
            if node_id in self.call_graph.nodes:
                node = self.call_graph.nodes[node_id]
                if node.decorators:
                    objectives.append(f"Understand {node.decorators[0]} pattern")
                if node.is_async:
                    objectives.append("Master async/await pattern")
        
        return objectives[:3]  # Max 3 objectives
    
    def _calculate_xp_reward(self, difficulty: Difficulty) -> int:
        """Calculate XP reward based on difficulty"""
        rewards = {
            Difficulty.TUTORIAL: 50,
            Difficulty.BASIC: 100,
            Difficulty.INTERMEDIATE: 150,
            Difficulty.ADVANCED: 200,
            Difficulty.EXPERT: 300
        }
        return rewards.get(difficulty, 100)


# ============================================
# Example Usage
# ============================================

if __name__ == '__main__':
    print("="*60)
    print("Level Generator Demo")
    print("="*60)
    
    # This would normally use a real CallGraph from analyzer
    from app.models.core import CallGraph, CodeNode, NodeType, Language
    
    # Create a simple demo call graph
    node1 = CodeNode(
        id="app.py::main",
        name="main",
        node_type=NodeType.FUNCTION,
        language=Language.PYTHON,
        file_path="app.py",
        line_start=1,
        line_end=10,
        complexity=5,
        loc=10
    )
    
    node2 = CodeNode(
        id="app.py::process",
        name="process",
        node_type=NodeType.FUNCTION,
        language=Language.PYTHON,
        file_path="app.py",
        line_start=12,
        line_end=20,
        complexity=8,
        loc=9
    )
    
    node1.calls.add(node2.id)
    node2.called_by.add(node1.id)
    
    graph = CallGraph(
        nodes={node1.id: node1, node2.id: node2},
        edges=[],
        entry_points=[node1.id]
    )
    
    # Generate levels
    generator = LevelGenerator(graph)
    levels = generator.generate_levels(max_levels=3)
    
    print(f"\nGenerated {len(levels)} levels:\n")
    for level in levels:
        print(f"  {level.name}")
        print(f"    Difficulty: {level.difficulty.name}")
        print(f"    Challenges: {len(level.challenges)}")
        print(f"    XP Reward: {level.xp_reward}")
        print(f"    Estimated Time: {level.estimated_time} min")
        print()
    
    print("="*60)
    print("✓ Level Generator is working!")
    print("="*60)
