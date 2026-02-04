#!/usr/bin/env python3
"""
Test Python Analyzer on Mini-Flask Example

This test demonstrates the analyzer's ability to extract and understand
the Mini-Flask codebase that users will later build in the mini project challenge.
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.analyzers.python_analyzer import PythonAnalyzer
from app.models.core import Language

def main():
    print("="*70)
    print("Testing Python Analyzer on Mini-Flask Example")
    print("="*70)
    
    # Analyze mini_flask.py
    mini_flask_path = Path(__file__).parent.parent / "examples"
    
    analyzer = PythonAnalyzer(mini_flask_path, Language.PYTHON)
    result = analyzer.analyze()
    
    print(f"\n📊 Analysis Results:")
    print(f"  Files: {result.files_analyzed}")
    print(f"  Total LOC: {result.lines_of_code}")
    print(f"  Analysis Time: {result.analysis_time:.3f}s")
    print(f"  Nodes: {result.call_graph.total_nodes}")
    print(f"  Edges: {result.call_graph.total_edges}")
    print(f"  Entry Points: {len(result.call_graph.entry_points)}")
    print(f"  Max Call Depth: {result.call_graph.max_depth}")
    
    # Show extracted classes
    print(f"\n📦 Classes Found:")
    classes = [n for n in result.call_graph.nodes.values() if n.node_type.value == 'class']
    for cls in classes:
        print(f"  - {cls.name} ({cls.loc} LOC, {cls.metadata.get('method_count', 0)} methods)")
    
    # Show entry points
    print(f"\n🎯 Entry Points:")
    for ep_id in result.call_graph.entry_points:
        if ep_id in result.call_graph.nodes:
            node = result.call_graph.nodes[ep_id]
            print(f"  - {node.name} ({Path(node.file_path).name}:{node.line_start})")
    
    # Show call graph sample
    print(f"\n🔗 Call Graph Sample (First 10 Edges):")
    for i, edge in enumerate(result.call_graph.edges[:10]):
        source_node = result.call_graph.nodes.get(edge.source)
        target_node = result.call_graph.nodes.get(edge.target)
        if source_node and target_node:
            print(f"  {i+1}. {source_node.name} → {target_node.name}")
    
    # Show functions with highest complexity
    print(f"\n⚡ Most Complex Functions:")
    functions = [n for n in result.call_graph.nodes.values() 
                if n.node_type.value in ['function', 'method']]
    sorted_functions = sorted(functions, key=lambda x: x.complexity, reverse=True)[:5]
    for i, func in enumerate(sorted_functions):
        print(f"  {i+1}. {func.name} (complexity: {func.complexity}, {func.loc} LOC)")
    
    # Identify potential learning levels
    print(f"\n🎓 Potential Learning Levels:")
    if result.call_graph.entry_points:
        entry_id = result.call_graph.entry_points[0]
        chains = result.call_graph.get_call_chain(entry_id, max_depth=5)
        print(f"  Found {len(chains)} call chains from entry point")
        if chains:
            print(f"  Sample chain: {' → '.join(chains[0][:5])}")
    
    # Validate result
    if result.is_valid:
        print(f"\n✅ Analysis is VALID")
    else:
        print(f"\n❌ Analysis has errors:")
        for error in result.errors:
            print(f"  - {error}")
    
    print(f"\n{'='*70}")
    print("✓ Test Complete!")
    print(f"{'='*70}\n")
    
    return result


if __name__ == '__main__':
    result = main()
