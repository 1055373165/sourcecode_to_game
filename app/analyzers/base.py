"""
Language Analyzer Interface

Defines the abstract base class that all language-specific analyzers must implement.
This ensures a consistent interface regardless of the source language (Python, Go, etc.).

Design Pattern: Strategy Pattern
- Each language has its own analyzer implementation
- All implement the same interface
- Can be swapped at runtime based on project language
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from pathlib import Path

from app.models.core import (
    CodeNode, CallGraph, AnalysisResult, Language,
    NodeType, Parameter
)


class ILanguageAnalyzer(ABC):
    """
    Abstract base class for language-specific code analyzers
    
    All language analyzers (PythonAnalyzer, GolangAnalyzer, etc.) must
    implement this interface to ensure consistent behavior.
    
    Lifecycle:
        1. __init__(project_path) - Initialize analyzer
        2. analyze() - Run full analysis
        3. get_result() - Retrieve AnalysisResult
    """
    
    def __init__(self, project_path: Path, language: Language):
        """
        Initialize the analyzer
        
        Args:
            project_path: Path to the project root directory
            language: Programming language of the project
        """
        self.project_path = project_path
        self.language = language
        self.result: Optional[AnalysisResult] = None
    
    @abstractmethod
    def analyze(self) -> AnalysisResult:
        """
        Perform complete code analysis
        
        This is the main entry point that orchestrates the entire analysis:
        1. Parse all source files
        2. Extract functions/classes
        3. Build call graph
        4. Identify entry points
        5. Calculate metrics
        
        Returns:
            AnalysisResult containing all extracted information
        
        Raises:
            AnalysisError: If analysis fails
        """
        pass
    
    @abstractmethod
    def parse_file(self, file_path: Path) -> List[CodeNode]:
        """
        Parse a single source file and extract code nodes
        
        Args:
            file_path: Path to source file
        
        Returns:
            List of CodeNode objects (functions, classes, etc.)
        
        Raises:
            ParseError: If file cannot be parsed
        """
        pass
    
    @abstractmethod
    def build_call_graph(self, nodes: List[CodeNode]) -> CallGraph:
        """
        Build call graph from extracted code nodes
        
        Analyzes function calls to construct the complete call graph,
        including determining which functions call which.
        
        Args:
            nodes: List of all CodeNode objects from the project
        
        Returns:
            CallGraph object with nodes and edges
        """
        pass
    
    @abstractmethod
    def identify_entry_points(self, nodes: List[CodeNode]) -> List[str]:
        """
        Identify entry point functions (main, handlers, etc.)
        
        Entry points are functions that serve as the start of execution:
        - main() functions
        - HTTP request handlers
        - CLI command handlers
        - Event handlers
        
        Args:
            nodes: All code nodes in the project
        
        Returns:
            List of CodeNode IDs that are entry points
        """
        pass
    
    @abstractmethod
    def calculate_complexity(self, node: CodeNode, source_code: str) -> int:
        """
        Calculate cyclomatic complexity for a code node
        
        Args:
            node: CodeNode to analyze
            source_code: Source code of the function
        
        Returns:
            Cyclomatic complexity score
        """
        pass
    
    # ============================================
    # Helper Methods (with default implementations)
    # ============================================
    
    def find_source_files(self) -> List[Path]:
        """
        Find all source files in the project
        
        Default implementation: recursively find files with language-specific extension
        Can be overridden for special cases
        
        Returns:
            List of source file paths
        """
        extensions = self._get_file_extensions()
        source_files = []
        
        for ext in extensions:
            source_files.extend(self.project_path.rglob(f"*{ext}"))
        
        return source_files
    
    @abstractmethod
    def _get_file_extensions(self) -> List[str]:
        """
        Get file extensions for this language
        
        Returns:
            List of extensions (e.g., ['.py'] for Python)
        """
        pass
    
    def get_result(self) -> Optional[AnalysisResult]:
        """
        Get the analysis result
        
        Returns:
            AnalysisResult if analysis has been run, None otherwise
        """
        return self.result
    
    def validate_result(self, result: AnalysisResult) -> bool:
        """
        Validate that analysis result is complete and correct
        
        Args:
            result: AnalysisResult to validate
        
        Returns:
            True if valid, False otherwise (sets errors in result)
        """
        errors = []
        
        # Check basic requirements
        if not result.call_graph.nodes:
            errors.append("No code nodes found")
        
        if not result.call_graph.entry_points:
            errors.append("No entry points identified")
        
        if result.call_graph.total_nodes == 0:
            errors.append("Call graph is empty")
        
        # Validate graph structure
        for edge in result.call_graph.edges:
            if edge.source not in result.call_graph.nodes:
                errors.append(f"Edge source not in nodes: {edge.source}")
            if edge.target not in result.call_graph.nodes:
                errors.append(f"Edge target not in nodes: {edge.target}")
        
        result.errors.extend(errors)
        result.is_valid = len(errors) == 0
        
        return result.is_valid


class AnalysisError(Exception):
    """Raised when code analysis fails"""
    pass


class ParseError(Exception):
    """Raised when file parsing fails"""
    pass


# ============================================
# Analyzer Factory
# ============================================

class AnalyzerFactory:
    """
    Factory for creating language-specific analyzers
    
    Usage:
        analyzer = AnalyzerFactory.create(Language.PYTHON, project_path)
        result = analyzer.analyze()
    """
    
    _analyzers: Dict[Language, type] = {}
    
    @classmethod
    def register(cls, language: Language, analyzer_class: type):
        """
        Register an analyzer implementation for a language
        
        Args:
            language: Language this analyzer handles
            analyzer_class: Class implementing ILanguageAnalyzer
        """
        cls._analyzers[language] = analyzer_class
    
    @classmethod
    def create(cls, language: Language, project_path: Path) -> ILanguageAnalyzer:
        """
        Create an analyzer for the specified language
        
        Args:
            language: Programming language to analyze
            project_path: Path to project root
        
        Returns:
            Instance of appropriate analyzer
        
        Raises:
            ValueError: If language is not supported
        """
        if language not in cls._analyzers:
            raise ValueError(f"No analyzer registered for {language}")
        
        analyzer_class = cls._analyzers[language]
        return analyzer_class(project_path, language)
    
    @classmethod
    def supported_languages(cls) -> List[Language]:
        """Get list of supported languages"""
        return list(cls._analyzers.keys())


# ============================================
# Example Usage
# ============================================

if __name__ == '__main__':
    print("="*60)
    print("Analyzer Interface Demo")
    print("="*60)
    
    # Show interface methods
    print("\nILanguageAnalyzer Interface:")
    print("  Required Methods:")
    for name, method in ILanguageAnalyzer.__dict__.items():
        if hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__:
            print(f"    - {name}()")
    
    print("\n  Helper Methods:")
    print("    - find_source_files()")
    print("    - get_result()")
    print("    - validate_result()")
    
    print("\nAnalyzerFactory:")
    print(f"  Supported languages: {AnalyzerFactory.supported_languages()}")
    print("  (Empty - implementations will register themselves)")
    
    print("\n" + "="*60)
    print("✓ Analyzer interface defined!")
    print("✓ Ready for Python/Golang implementations")
    print("="*60)
