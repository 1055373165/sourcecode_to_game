#!/usr/bin/env python3
"""
Benchmark Python call graph generation tools

This script evaluates different approaches to building call graphs:
1. Custom implementation using `ast`
2. `pyan3` (if installed)
3. Manual validation of accuracy
"""

import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class CallGraphNode:
    """Represents a function in the call graph"""
    name: str
    file_path: str
    line_number: int
    calls: Set[str] = field(default_factory=set)
    called_by: Set[str] = field(default_factory=set)


class CallGraphBuilder:
    """Build call graph using Python's ast module"""
    
    def __init__(self):
        self.nodes: Dict[str, CallGraphNode] = {}
        self.current_function: str = None
    
    def analyze_file(self, file_path: Path) -> None:
        """Analyze a Python file and extract call graph"""
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        try:
            tree = ast.parse(source, filename=str(file_path))
            self._visit_node(tree, str(file_path))
        except SyntaxError as e:
            print(f"⚠️  Syntax error in {file_path}: {e}")
    
    def _visit_node(self, node: ast.AST, file_path: str) -> None:
        """Recursively visit AST nodes"""
        if isinstance(node, ast.FunctionDef):
            self._handle_function_def(node, file_path)
        elif isinstance(node, ast.Call):
            self._handle_call(node)
        
        # Recurse into child nodes
        for child in ast.iter_child_nodes(node):
            self._visit_node(child, file_path)
    
    def _handle_function_def(self, node: ast.FunctionDef, file_path: str) -> None:
        """Handle function definition"""
        func_name = node.name
        
        # Create node if doesn't exist
        if func_name not in self.nodes:
            self.nodes[func_name] = CallGraphNode(
                name=func_name,
                file_path=file_path,
                line_number=node.lineno
            )
        
        # Set current function context
        prev_function = self.current_function
        self.current_function = func_name
        
        # Visit function body
        for stmt in node.body:
            self._visit_node(stmt, file_path)
        
        # Restore previous context
        self.current_function = prev_function
    
    def _handle_call(self, node: ast.Call) -> None:
        """Handle function call"""
        if self.current_function is None:
            return
        
        # Extract called function name
        called_func = None
        
        if isinstance(node.func, ast.Name):
            # Simple function call: foo()
            called_func = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # Method call: obj.foo()
            called_func = node.func.attr
        
        if called_func:
            # Add to current function's calls
            self.nodes[self.current_function].calls.add(called_func)
            
            # Create called function node if doesn't exist
            if called_func not in self.nodes:
                self.nodes[called_func] = CallGraphNode(
                    name=called_func,
                    file_path="unknown",
                    line_number=0
                )
            
            # Add reverse edge
            self.nodes[called_func].called_by.add(self.current_function)
    
    def get_call_chain(self, entry_point: str, max_depth: int = 10) -> List[List[str]]:
        """Get all call chains starting from entry point"""
        if entry_point not in self.nodes:
            return []
        
        chains = []
        visited = set()
        
        def dfs(node_name: str, chain: List[str], depth: int):
            if depth > max_depth or node_name in visited:
                return
            
            visited.add(node_name)
            chain.append(node_name)
            
            node = self.nodes.get(node_name)
            if not node or not node.calls:
                # Leaf node - save chain
                chains.append(chain.copy())
            else:
                # Continue exploring
                for called in node.calls:
                    dfs(called, chain.copy(), depth + 1)
            
            visited.remove(node_name)
        
        dfs(entry_point, [], 0)
        return chains
    
    def print_graph(self) -> None:
        """Print call graph in a readable format"""
        print(f"\n{'='*70}")
        print(f"CALL GRAPH ({len(self.nodes)} nodes)")
        print(f"{'='*70}\n")
        
        for name, node in sorted(self.nodes.items()):
            if node.calls:
                print(f"📦 {name} ({node.file_path}:{node.line_number})")
                for called in sorted(node.calls):
                    print(f"   └─> {called}")
                print()
    
    def export_dot(self, output_file: Path) -> None:
        """Export call graph to GraphViz DOT format"""
        lines = ["digraph CallGraph {"]
        lines.append('  node [shape=box];')
        
        for name, node in self.nodes.items():
            for called in node.calls:
                lines.append(f'  "{name}" -> "{called}";')
        
        lines.append("}")
        
        output_file.write_text('\n'.join(lines))
        print(f"✓ Exported call graph to {output_file}")


def demo_call_graph():
    """Demo: Build call graph from sample code"""
    sample_code = '''
def main():
    """Entry point"""
    result = process_data()
    save_result(result)

def process_data():
    """Process data"""
    raw = load_data()
    cleaned = clean_data(raw)
    return validate(cleaned)

def load_data():
    """Load data from file"""
    return []

def clean_data(data):
    """Clean data"""
    return [x for x in data if x]

def validate(data):
    """Validate data"""
    return data

def save_result(data):
    """Save result"""
    write_to_file(data)

def write_to_file(data):
    """Write to file"""
    pass
'''
    
    # Create sample file
    sample_file = Path("sample_calls.py")
    sample_file.write_text(sample_code)
    
    # Build call graph
    builder = CallGraphBuilder()
    builder.analyze_file(sample_file)
    
    # Print graph
    builder.print_graph()
    
    # Get call chains from main
    print(f"{'='*70}")
    print("CALL CHAINS FROM 'main'")
    print(f"{'='*70}\n")
    
    chains = builder.get_call_chain("main")
    for i, chain in enumerate(chains, 1):
        print(f"Chain {i}: {' -> '.join(chain)}")
    
    # Export to DOT format
    dot_file = Path("callgraph.dot")
    builder.export_dot(dot_file)
    
    # Cleanup
    sample_file.unlink()
    
    print(f"\n💡 To visualize the graph:")
    print(f"   dot -Tpng {dot_file} -o callgraph.png")
    print(f"   open callgraph.png")


def benchmark_accuracy():
    """Benchmark call graph accuracy"""
    # Create test case with known call graph
    test_code = '''
def func_a():
    func_b()
    func_c()

def func_b():
    func_d()

def func_c():
    func_d()

def func_d():
    pass
'''
    
    # Expected call graph
    expected = {
        'func_a': {'func_b', 'func_c'},
        'func_b': {'func_d'},
        'func_c': {'func_d'},
        'func_d': set()
    }
    
    # Build actual call graph
    test_file = Path("test_calls.py")
    test_file.write_text(test_code)
    
    builder = CallGraphBuilder()
    builder.analyze_file(test_file)
    
    # Compare
    print(f"\n{'='*70}")
    print("ACCURACY TEST")
    print(f"{'='*70}\n")
    
    total_edges = 0
    correct_edges = 0
    
    for func_name, expected_calls in expected.items():
        actual_calls = builder.nodes.get(func_name, CallGraphNode("", "", 0)).calls
        
        total_edges += len(expected_calls)
        correct_edges += len(expected_calls & actual_calls)
        
        status = "✓" if expected_calls == actual_calls else "✗"
        print(f"{status} {func_name}")
        print(f"   Expected: {expected_calls}")
        print(f"   Actual:   {actual_calls}")
    
    accuracy = (correct_edges / total_edges * 100) if total_edges > 0 else 0
    print(f"\nAccuracy: {correct_edges}/{total_edges} edges ({accuracy:.1f}%)")
    
    # Cleanup
    test_file.unlink()


if __name__ == "__main__":
    print("Call Graph Benchmark Tool\n")
    
    # Demo
    demo_call_graph()
    
    # Accuracy test
    benchmark_accuracy()
    
    print("\n💡 Next Steps:")
    print("1. Test on real projects (Flask, requests)")
    print("2. Compare with pyan3 output")
    print("3. Handle edge cases: decorators, lambdas, dynamic calls")
    print("4. Measure performance on large codebases")
