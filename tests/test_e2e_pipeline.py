#!/usr/bin/env python3
"""
End-to-End Test: Analyzer + Level Generator

This test demonstrates the complete pipeline:
1. Analyze Python codebase (Mini-Flask)
2. Generate learning levels from call graph
3. Display generated levels
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.analyzers.python_analyzer import PythonAnalyzer
from app.generators.level_generator import LevelGenerator
from app.models.core import Language

def main():
    print("="*70)
    print("End-to-End Test: Analyzer → Level Generator")
    print("="*70)
    
    # Step 1: Analyze Mini-Flask
    print("\n📊 Step 1: Analyzing Mini-Flask...")
    mini_flask_path = Path(__file__).parent.parent / "examples"
    
    analyzer = PythonAnalyzer(mini_flask_path, Language.PYTHON)
    result = analyzer.analyze()
    
    print(f"  ✓ Analyzed {result.files_analyzed} files")
    print(f"  ✓ Extracted {result.call_graph.total_nodes} nodes")
    print(f"  ✓ Built {result.call_graph.total_edges} edges")
    print(f"  ✓ Found {len(result.call_graph.entry_points)} entry points")
    
    # Step 2: Generate Levels
    print("\n🎮 Step 2: Generating Learning Levels...")
    generator = LevelGenerator(result.call_graph)
    levels = generator.generate_levels(max_levels=5)
    
    print(f"  ✓ Generated {len(levels)} levels")
    
    # Step 3: Display Levels
    print("\n📚 Generated Learning Levels:\n")
    print(f"{'='*70}")
    
    for i, level in enumerate(levels, 1):
        print(f"\nLevel {i}: {level.name}")
        print(f"├─ Difficulty: {level.difficulty.name} ({level.difficulty.value}/5)")
        print(f"├─ Call Chain: {len(level.call_chain)} functions")
        
        if level.call_chain:
            chain_names = []
            for node_id in level.call_chain[:3]:
                if node_id in result.call_graph.nodes:
                    chain_names.append(result.call_graph.nodes[node_id].name)
            if len(level.call_chain) > 3:
                chain_names.append(f"...+{len(level.call_chain)-3} more")
            print(f"│  └─ {' → '.join(chain_names)}")
        
        print(f"├─ Challenges: {len(level.challenges)}")
        for j, challenge in enumerate(level.challenges, 1):
            print(f"│  {j}. {challenge.type.value} ({challenge.points} pts)")
        
        print(f"├─ Learning Objectives:")
        for obj in level.objectives:
            print(f"│  • {obj}")
        
        print(f"├─ Rewards:")
        print(f"│  • {level.xp_reward} XP")
        print(f"└─ Estimated Time: {level.estimated_time} minutes")
        print(f"{'-'*70}")
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 Pipeline Summary:")
    print(f"{'='*70}")
    
    total_xp = sum(level.xp_reward for level in levels)
    total_time = sum(level.estimated_time for level in levels)
    total_challenges = sum(len(level.challenges) for level in levels)
    
    print(f"  Levels Generated: {len(levels)}")
    print(f"  Total Challenges: {total_challenges}")
    print(f"  Total XP Available: {total_xp}")
    print(f"  Estimated Time to Complete: {total_time} minutes ({total_time/60:.1f} hours)")
    
    # Difficulty distribution
    print(f"\n  Difficulty Distribution:")
    from collections import Counter
    difficulty_counts = Counter(level.difficulty.name for level in levels)
    for diff, count in sorted(difficulty_counts.items()):
        print(f"    {diff}: {count} levels")
    
    # Challenge type distribution
    print(f"\n  Challenge Type Distribution:")
    challenge_type_counts = Counter()
    for level in levels:
        for challenge in level.challenges:
            challenge_type_counts[challenge.type.value] += 1
    
    for ctype, count in sorted(challenge_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {ctype}: {count}")
    
    print(f"\n{'='*70}")
    print("✅ End-to-End Pipeline Working Successfully!")
    print(f"{'='*70}\n")
    
    return levels


if __name__ == '__main__':
    levels = main()
