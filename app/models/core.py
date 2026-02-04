"""
Core Data Models - Language-Agnostic Abstractions

This module defines the core data models used throughout the platform.
These models are language-agnostic and provide a unified interface for
representing code structure regardless of source language (Python, Golang, etc.).

Design Principles:
1. Language Agnostic: Same models work for Python, Go, and future languages
2. Serializable: JSON-compatible for API and database storage
3. Type Safe: Use dataclasses with type hints
4. Immutable Where Possible: Use frozen dataclasses for safety
5. Rich Metadata: Include all info needed for level generation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
from enum import Enum
from datetime import datetime


# ============================================
# Enums
# ============================================

class Language(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    GOLANG = "golang"


class ChallengeType(str, Enum):
    """Types of challenges we can generate"""
    MULTIPLE_CHOICE = "multiple_choice"
    CODE_TRACING = "code_tracing"
    FILL_BLANK = "fill_blank"
    CODE_COMPLETION = "code_completion"
    DEBUGGING = "debugging"
    ARCHITECTURE = "architecture"
    MINI_PROJECT = "mini_project"


class NodeType(str, Enum):
    """Types of code nodes"""
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    INTERFACE = "interface"
    MODULE = "module"


class Difficulty(int, Enum):
    """Difficulty levels"""
    TUTORIAL = 1
    BASIC = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5


# ============================================
# Core Code Representation
# ============================================

@dataclass(frozen=True)
class Parameter:
    """Function/method parameter"""
    name: str
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type_hint,
            'default': self.default_value
        }


@dataclass
class CodeNode:
    """
    Language-agnostic representation of a code element
    
    Represents functions, methods, classes, etc. regardless of source language.
    Contains all metadata needed for analysis and level generation.
    """
    
    # Identity
    id: str  # Unique identifier: "file.py::ClassName.method_name"
    name: str  # Function/class name
    node_type: NodeType
    language: Language
    
    # Location
    file_path: str
    line_start: int
    line_end: int
    
    # Signature
    parameters: List[Parameter] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    
    # Relationships
    calls: Set[str] = field(default_factory=set)  # IDs of functions this calls
    called_by: Set[str] = field(default_factory=set)  # IDs of functions that call this
    depends_on: Set[str] = field(default_factory=set)  # Module/import dependencies
    
    # Metadata
    docstring: Optional[str] = None
    is_exported: bool = True  # Public vs private
    is_async: bool = False
    is_generator: bool = False
    
    # Metrics
    complexity: int = 1  # Cyclomatic complexity
    loc: int = 0  # Lines of code
    
    # Additional metadata (language-specific)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.node_type.value,
            'language': self.language.value,
            'file_path': self.file_path,
            'line_start': self.line_start,
            'line_end': self.line_end,
            'parameters': [p.to_dict() for p in self.parameters],
            'return_type': self.return_type,
            'decorators': self.decorators,
            'calls': list(self.calls),
            'called_by': list(self.called_by),
            'depends_on': list(self.depends_on),
            'docstring': self.docstring,
            'is_exported': self.is_exported,
            'is_async': self.is_async,
            'is_generator': self.is_generator,
            'complexity': self.complexity,
            'loc': self.loc,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeNode':
        """Deserialize from dict"""
        return cls(
            id=data['id'],
            name=data['name'],
            node_type=NodeType(data['type']),
            language=Language(data['language']),
            file_path=data['file_path'],
            line_start=data['line_start'],
            line_end=data['line_end'],
            parameters=[Parameter(**p) for p in data.get('parameters', [])],
            return_type=data.get('return_type'),
            decorators=data.get('decorators', []),
            calls=set(data.get('calls', [])),
            called_by=set(data.get('called_by', [])),
            depends_on=set(data.get('depends_on', [])),
            docstring=data.get('docstring'),
            is_exported=data.get('is_exported', True),
            is_async=data.get('is_async', False),
            is_generator=data.get('is_generator', False),
            complexity=data.get('complexity', 1),
            loc=data.get('loc', 0),
            metadata=data.get('metadata', {})
        )


@dataclass
class CallEdge:
    """Represents a function call relationship"""
    source: str  # Calling function ID
    target: str  # Called function ID
    call_type: str = "direct"  # direct, indirect, polymorphic
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'target': self.target,
            'call_type': self.call_type,
            'line_number': self.line_number
        }


@dataclass
class CallGraph:
    """
    Call graph representation
    
    Stores the complete call graph for a project with all nodes and edges.
    Provides methods for traversal, analysis, and serialization.
    """
    
    nodes: Dict[str, CodeNode]  # node_id -> CodeNode
    edges: List[CallEdge]
    entry_points: List[str]  # IDs of entry point functions (main, handlers, etc.)
    
    # Graph metadata
    total_nodes: int = 0
    total_edges: int = 0
    max_depth: int = 0
    
    def __post_init__(self):
        """Calculate derived metrics"""
        self.total_nodes = len(self.nodes)
        self.total_edges = len(self.edges)
        self.max_depth = self._calculate_max_depth()
    
    def _calculate_max_depth(self) -> int:
        """Calculate maximum call chain depth"""
        if not self.entry_points:
            return 0
        
        max_depth = 0
        for entry_id in self.entry_points:
            depth = self._dfs_depth(entry_id, visited=set())
            max_depth = max(max_depth, depth)
        return max_depth
    
    def _dfs_depth(self, node_id: str, visited: Set[str], depth: int = 0) -> int:
        """DFS to find maximum depth from a node"""
        if node_id in visited or node_id not in self.nodes:
            return depth
        
        visited.add(node_id)
        node = self.nodes[node_id]
        
        if not node.calls:
            return depth
        
        max_child_depth = depth
        for called_id in node.calls:
            child_depth = self._dfs_depth(called_id, visited.copy(), depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def get_call_chain(self, entry_id: str, max_depth: int = 10) -> List[List[str]]:
        """
        Get all call chains from an entry point
        
        Returns:
            List of chains, where each chain is a list of node IDs
        """
        chains = []
        
        def dfs(node_id: str, chain: List[str], visited: Set[str]):
            if len(chain) > max_depth or node_id in visited:
                return
            
            if node_id not in self.nodes:
                return
            
            visited.add(node_id)
            chain.append(node_id)
            node = self.nodes[node_id]
            
            if not node.calls:
                # Leaf node - save chain
                chains.append(chain.copy())
            else:
                for called_id in node.calls:
                    dfs(called_id, chain.copy(), visited.copy())
        
        dfs(entry_id, [], set())
        return chains
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to JSON-compatible dict"""
        return {
            'nodes': {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            'edges': [edge.to_dict() for edge in self.edges],
            'entry_points': self.entry_points,
            'total_nodes': self.total_nodes,
            'total_edges': self.total_edges,
            'max_depth': self.max_depth
        }
    
    def to_dot(self) -> str:
        """Export to GraphViz DOT format for visualization"""
        lines = ['digraph CallGraph {']
        lines.append('  rankdir=LR;')
        lines.append('  node [shape=box, style=rounded];')
        
        # Entry points in green
        for entry_id in self.entry_points:
            if entry_id in self.nodes:
                name = self.nodes[entry_id].name
                lines.append(f'  "{entry_id}" [label="{name}", fillcolor=lightgreen, style=filled];')
        
        # Edges
        for edge in self.edges:
            style = "solid" if edge.call_type == "direct" else "dashed"
            lines.append(f'  "{edge.source}" -> "{edge.target}" [style={style}];')
        
        lines.append('}')
        return '\n'.join(lines)


# ============================================
# Level & Challenge Models
# ============================================

@dataclass
class Level:
    """
    Represents a learning level/challenge
    
    Each level focuses on understanding a specific part of the call chain.
    """
    
    id: str
    name: str
    description: str
    difficulty: Difficulty
    
    # Associated code
    entry_function: str  # CodeNode ID
    call_chain: List[str]  # List of CodeNode IDs in the chain
    code_snippet: str  # Relevant code to display
    
    # Challenges in this level
    challenges: List['Challenge'] = field(default_factory=list)
    
    # Learning objectives
    objectives: List[str] = field(default_factory=list)
    
    # Rewards
    xp_reward: int = 100
    estimated_time: int = 15  # minutes
    
    # Prerequisites
    prerequisites: List[str] = field(default_factory=list)  # Level IDs
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'difficulty': self.difficulty.value,
            'entry_function': self.entry_function,
            'call_chain': self.call_chain,
            'code_snippet': self.code_snippet,
            'challenges': [c.to_dict() for c in self.challenges],
            'objectives': self.objectives,
            'xp_reward': self.xp_reward,
            'estimated_time': self.estimated_time,
            'prerequisites': self.prerequisites
        }


@dataclass
class Challenge:
    """Individual challenge within a level"""
    
    id: str
    type: ChallengeType
    question: Dict[str, Any]  # Question data (format depends on type)
    answer: Dict[str, Any]  # Expected answer
    hints: List[str] = field(default_factory=list)
    points: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type.value,
            'question': self.question,
            'answer': self.answer,
            'hints': self.hints,
            'points': self.points
        }


# ============================================
# Project Analysis Result
# ============================================

@dataclass
class AnalysisResult:
    """
    Complete analysis result for a project
    
    This is the output of the analyzer service, containing all extracted
    information about the codebase.
    """
    
    project_id: str
    language: Language
    call_graph: CallGraph
    levels: List[Level] = field(default_factory=list)
    
    # Analysis metadata
    analyzed_at: datetime = field(default_factory=datetime.now)
    analysis_time: float = 0.0  # seconds
    files_analyzed: int = 0
    lines_of_code: int = 0
    
    # Validation
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'project_id': self.project_id,
            'language': self.language.value,
            'call_graph': self.call_graph.to_dict(),
            'levels': [level.to_dict() for level in self.levels],
            'analyzed_at': self.analyzed_at.isoformat(),
            'analysis_time': self.analysis_time,
            'files_analyzed': self.files_analyzed,
            'lines_of_code': self.lines_of_code,
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings
        }


# ============================================
# Example Usage
# ============================================

if __name__ == '__main__':
    # Demo creating models
    print("="*60)
    print("Data Models Demo")
    print("="*60)
    
    # Create a code node
    node = CodeNode(
        id="app.py::Flask.__call__",
        name="__call__",
        node_type=NodeType.METHOD,
        language=Language.PYTHON,
        file_path="/path/to/flask/app.py",
        line_start=100,
        line_end=150,
        parameters=[
            Parameter(name="self"),
            Parameter(name="environ", type_hint="dict"),
            Parameter(name="start_response", type_hint="Callable")
        ],
        return_type="Response",
        complexity=15,
        loc=50
    )
    
    print(f"\nCodeNode created: {node.name}")
    print(f"  Type: {node.node_type.value}")
    print(f"  Parameters: {len(node.parameters)}")
    print(f"  Complexity: {node.complexity}")
    
    # Serialize
    node_dict = node.to_dict()
    print(f"\n  Serialized keys: {list(node_dict.keys())}")
    
    # Create call graph
    nodes = {node.id: node}
    edges = [CallEdge(source=node.id, target="app.py::Flask.process_request")]
    graph = CallGraph(
        nodes=nodes,
        edges=edges,
        entry_points=[node.id]
    )
    
    print(f"\nCallGraph created:")
    print(f"  Nodes: {graph.total_nodes}")
    print(f"  Edges: {graph.total_edges}")
    print(f"  Max depth: {graph.max_depth}")
    
    print("\n" + "="*60)
    print("✓ Data models are fully functional!")
    print("="*60)
