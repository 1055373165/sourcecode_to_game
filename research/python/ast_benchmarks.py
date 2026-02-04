#!/usr/bin/env python3
"""
Benchmark Python AST parsing tools

This script evaluates:
1. Python's built-in `ast` module
2. `astroid` (if installed)
3. Parse time, memory usage, and extraction accuracy
"""

import ast
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ParseResult:
    """Result of parsing a Python file"""
    file_path: str
    parse_time: float  # seconds
    memory_used: float  # MB
    num_functions: int
    num_classes: int
    num_imports: int
    success: bool
    error: str = ""


class ASTBenchmark:
    """Benchmark Python AST parsing"""
    
    def __init__(self):
        self.results: List[ParseResult] = []
    
    def parse_with_ast(self, file_path: Path) -> ParseResult:
        """Parse using Python's built-in ast module"""
        tracemalloc.start()
        start_time = time.time()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            # Extract statistics
            num_functions = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.FunctionDef))
            num_classes = sum(1 for _ in ast.walk(tree) if isinstance(_, ast.ClassDef))
            num_imports = sum(1 for _ in ast.walk(tree) 
                            if isinstance(_, (ast.Import, ast.ImportFrom)))
            
            end_time = time.time()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            return ParseResult(
                file_path=str(file_path),
                parse_time=end_time - start_time,
                memory_used=peak / 1024 / 1024,  # Convert to MB
                num_functions=num_functions,
                num_classes=num_classes,
                num_imports=num_imports,
                success=True
            )
        
        except Exception as e:
            tracemalloc.stop()
            return ParseResult(
                file_path=str(file_path),
                parse_time=time.time() - start_time,
                memory_used=0,
                num_functions=0,
                num_classes=0,
                num_imports=0,
                success=False,
                error=str(e)
            )
    
    def extract_function_signatures(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract detailed function signatures"""
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source, filename=str(file_path))
        
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Extract parameters
                params = []
                for arg in node.args.args:
                    param_info = {
                        'name': arg.arg,
                        'annotation': ast.unparse(arg.annotation) if arg.annotation else None
                    }
                    params.append(param_info)
                
                # Extract return type
                return_type = ast.unparse(node.returns) if node.returns else None
                
                # Extract decorators
                decorators = [ast.unparse(dec) for dec in node.decorator_list]
                
                # Check if async
                is_async = isinstance(node, ast.AsyncFunctionDef)
                
                functions.append({
                    'name': node.name,
                    'params': params,
                    'return_type': return_type,
                    'decorators': decorators,
                    'is_async': is_async,
                    'line_start': node.lineno,
                    'line_end': node.end_lineno,
                    'docstring': ast.get_docstring(node)
                })
        
        return functions
    
    def benchmark_directory(self, directory: Path) -> None:
        """Benchmark all Python files in a directory"""
        python_files = list(directory.rglob("*.py"))
        
        print(f"\n{'='*70}")
        print(f"Benchmarking {len(python_files)} Python files in {directory}")
        print(f"{'='*70}\n")
        
        for file_path in python_files:
            result = self.parse_with_ast(file_path)
            self.results.append(result)
            
            status = "✓" if result.success else "✗"
            print(f"{status} {file_path.name:40s} "
                  f"Time: {result.parse_time*1000:6.2f}ms "
                  f"Mem: {result.memory_used:5.2f}MB "
                  f"Funcs: {result.num_functions:3d} "
                  f"Classes: {result.num_classes:3d}")
            
            if not result.success:
                print(f"  Error: {result.error}")
    
    def print_summary(self) -> None:
        """Print benchmark summary statistics"""
        if not self.results:
            print("No results to summarize")
            return
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        total_time = sum(r.parse_time for r in successful)
        avg_time = total_time / len(successful) if successful else 0
        max_time = max((r.parse_time for r in successful), default=0)
        
        total_memory = sum(r.memory_used for r in successful)
        avg_memory = total_memory / len(successful) if successful else 0
        
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"Total files:        {len(self.results)}")
        print(f"Successful:         {len(successful)}")
        print(f"Failed:             {len(failed)}")
        print(f"Total parse time:   {total_time:.3f}s")
        print(f"Average parse time: {avg_time*1000:.2f}ms")
        print(f"Max parse time:     {max_time*1000:.2f}ms")
        print(f"Average memory:     {avg_memory:.2f}MB")
        print(f"{'='*70}\n")


def demo_function_extraction():
    """Demo: Extract function signatures from a sample file"""
    # Create a sample Python file
    sample_code = '''
from typing import List, Optional

def greet(name: str, age: int = 0) -> str:
    """Greet a person"""
    return f"Hello {name}, age {age}"

async def fetch_data(url: str) -> dict:
    """Fetch data from URL"""
    pass

@property
def value(self) -> int:
    """Get value"""
    return self._value

class Calculator:
    def add(self, a: int, b: int) -> int:
        """Add two numbers"""
        return a + b
'''
    
    sample_file = Path("sample_code.py")
    sample_file.write_text(sample_code)
    
    benchmark = ASTBenchmark()
    functions = benchmark.extract_function_signatures(sample_file)
    
    print(f"\n{'='*70}")
    print("FUNCTION SIGNATURE EXTRACTION DEMO")
    print(f"{'='*70}\n")
    
    for func in functions:
        print(f"Function: {func['name']}")
        print(f"  Parameters: {func['params']}")
        print(f"  Return type: {func['return_type']}")
        print(f"  Decorators: {func['decorators']}")
        print(f"  Async: {func['is_async']}")
        print(f"  Lines: {func['line_start']}-{func['line_end']}")
        print(f"  Docstring: {func['docstring']}")
        print()
    
    # Cleanup
    sample_file.unlink()


if __name__ == "__main__":
    # Demo function extraction
    demo_function_extraction()
    
    # Benchmark current directory
    benchmark = ASTBenchmark()
    benchmark.benchmark_directory(Path("."))
    benchmark.print_summary()
    
    print("\n💡 Next Steps:")
    print("1. Download Flask source code and benchmark")
    print("2. Compare with `astroid` library")
    print("3. Test on larger codebases (1000+ LOC files)")
    print("4. Measure accuracy of type inference")
