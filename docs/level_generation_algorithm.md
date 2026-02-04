# Level Generation Algorithm Design

## Overview

The Level Generator is responsible for automatically creating engaging learning levels from analyzed codebases. It transforms call graphs and code metrics into structured learning experiences.

## Design Goals

1. **Automatic Generation**: Minimal manual intervention required
2. **Progressive Difficulty**: Levels increase in complexity naturally
3. **Focused Learning**: Each level teaches one clear concept
4. **Diverse Challenges**: Mix of challenge types keeps it engaging
5. **Scalable**: Works for projects of varying sizes (100-10,000 LOC)

## Architecture

```
CallGraph → LevelGenerator → List[Level]
              ↓
        [1] Identify Core Chains
        [2] Score Difficulty  
        [3] Select Challenge Types
        [4] Generate Questions
        [5] Add Hints & Objectives
```

## Algorithm Phases

### Phase 1: Core Chain Identification

**Goal**: Find the most important execution paths to teach

**Algorithm**:
```python
def identify_core_chains(call_graph: CallGraph) -> List[List[str]]:
    """
    Identify core call chains using weighted criteria
    
    Criteria (weighted):
    - Entry point proximity (40%): Closer to entry = more important
    - Call frequency (30%): More callers = more central
    - Code complexity (20%): Higher complexity = worth teaching
    - Documentation quality (10%): Better docs = better learning
    
    Returns:
        List of call chains, ordered by importance
    """
    chains = []
    
    for entry_id in call_graph.entry_points:
        # Get all chains from this entry point
        entry_chains = call_graph.get_call_chain(entry_id, max_depth=5)
        
        for chain in entry_chains:
            score = calculate_chain_importance(chain, call_graph)
            chains.append((score, chain))
    
    # Sort by score (descending)
    chains.sort(reverse=True, key=lambda x: x[0])
    
    # Return top N chains
    return [chain for score, chain in chains[:10]]


def calculate_chain_importance(chain: List[str], graph: CallGraph) -> float:
    """Calculate importance score for a call chain"""
    score = 0.0
    
    # Entry point proximity (40 points max)
    # First function in chain gets full score, decays exponentially
    for i, node_id in enumerate(chain):
        proximity_score = 40 * (0.7 ** i)
        score += proximity_score
    
    # Call frequency (30 points max)
    avg_called_by = sum(len(graph.nodes[id].called_by) for id in chain) / len(chain)
    frequency_score = min(30, avg_called_by * 5)
    score += frequency_score
    
    # Code complexity (20 points max)
    avg_complexity = sum(graph.nodes[id].complexity for id in chain) / len(chain)
    complexity_score = min(20, avg_complexity)
    score += complexity_score
    
    # Documentation quality (10 points max)
    documented_nodes = sum(1 for id in chain if graph.nodes[id].docstring)
    doc_score = (documented_nodes / len(chain)) * 10
    score += doc_score
    
    return score
```

**Example Output**:
```python
# Flask example
core_chains = [
    ['Flask.__call__', 'Flask.wsgi_app', 'Flask.full_dispatch_request'],
    ['Flask.route', 'Flask.add_url_rule', 'Map.add'],
    ['Request.__init__', 'Request.from_values', 'EnvironBuilder.get_environ']
]
```

### Phase 2: Difficulty Scoring

**Goal**: Assign difficulty level to each chain

**Algorithm**:
```python
def calculate_difficulty(chain: List[str], graph: CallGraph) -> Difficulty:
    """
    Calculate difficulty based on multiple factors
    
    Factors:
    - Chain length: Longer = harder
    - Avg complexity: Higher cyclomatic complexity = harder
    - Abstraction level: More OOP patterns = harder
    - Dependency count: More external deps = harder
    """
    score = 0
    
    # Chain length (0-20 points)
    length_score = min(20, len(chain) * 4)
    score += length_score
    
    # Average complexity (0-30 points)
    avg_complexity = sum(graph.nodes[id].complexity for id in chain) / len(chain)
    complexity_score = min(30, avg_complexity * 2)
    score += complexity_score
    
    # Abstraction level (0-25 points)
    # Count decorators, async, generators, etc.
    abstraction_score = 0
    for node_id in chain:
        node = graph.nodes[node_id]
        if node.decorators:
            abstraction_score += len(node.decorators) * 3
        if node.is_async:
            abstraction_score += 5
        if node.is_generator:
            abstraction_score += 5
    abstraction_score = min(25, abstraction_score)
    score += abstraction_score
    
    # Dependencies (0-25 points)
    total_deps = sum(len(graph.nodes[id].depends_on) for id in chain)
    dep_score = min(25, total_deps * 2)
    score += dep_score
    
    # Map score to difficulty enum
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
```

**Difficulty Mapping**:
| Score Range | Difficulty | Description |
|-------------|-----------|-------------|
| 0-19 | Tutorial | Single function, simple logic |
| 20-39 | Basic | 2-3 functions, basic control flow |
| 40-59 | Intermediate | 3-4 functions, OOP, error handling |
| 60-79 | Advanced | 4-5 functions, decorators, async |
| 80+ | Expert | 5+ functions, advanced patterns |

### Phase 3: Challenge Type Selection

**Goal**: Select appropriate challenge types for the level

**Algorithm**:
```python
def select_challenge_types(
    chain: List[str],
    difficulty: Difficulty,
    graph: CallGraph
) -> List[ChallengeType]:
    """
    Select 3-5 challenge types that fit the code characteristics
    
    Selection Strategy:
    - Always include Multiple Choice (baseline comprehension)
    - Code Tracing for chains with 3+ functions
    - Fill Blank for code with clear patterns
    - Code Completion for isolated functions
    - Debugging for complex logic (complexity > 10)
    - Architecture for design pattern usage
    """
    challenges = []
    
    # Always include Multiple Choice
    challenges.append(ChallengeType.MULTIPLE_CHOICE)
    
    # Code Tracing for longer chains
    if len(chain) >= 3:
        challenges.append(ChallengeType.CODE_TRACING)
    
    # Get chain characteristics
    avg_complexity = sum(graph.nodes[id].complexity for id in chain) / len(chain)
    has_decorators = any(graph.nodes[id].decorators for id in chain)
    has_async = any(graph.nodes[id].is_async for id in chain)
    
    # Fill Blank for pattern-heavy code
    if has_decorators or difficulty >= Difficulty.INTERMEDIATE:
        challenges.append(ChallengeType.FILL_BLANK)
    
    # Code Completion for intermediate+
    if difficulty >= Difficulty.INTERMEDIATE:
        challenges.append(ChallengeType.CODE_COMPLETION)
    
    # Debugging for complex functions
    if avg_complexity > 10:
        challenges.append(ChallengeType.DEBUGGING)
    
    # Architecture questions for expert levels
    if difficulty >= Difficulty.ADVANCED:
        challenges.append(ChallengeType.ARCHITECTURE)
    
    # Ensure 3-5 challenges
    return challenges[:5]
```

### Phase 4: Question Generation

**Goal**: Generate specific questions for each challenge type

**Templates by Type**:

#### Multiple Choice Template
```python
def generate_multiple_choice(node: CodeNode, graph: CallGraph) -> Challenge:
    """Generate MC question"""
    templates = [
        {
            'question': f"What does {node.name}() return?",
            'correct': node.return_type or "None",
            'distractors': ['str', 'dict', 'list', 'object']
        },
        {
            'question': f"How many parameters does {node.name}() accept?",
            'correct': str(len(node.parameters)),
            'distractors': [str(len(node.parameters) + i) for i in [-1, 1, 2]]
        },
        {
            'question': f"Which function does {node.name}() call first?",
            'correct': list(node.calls)[0] if node.calls else "None",
            'distractors': generate_plausible_functions(graph)
        }
    ]
    
    template = random.choice(templates)
    return create_mc_challenge(template)
```

#### Code Tracing Template
```python
def generate_code_tracing(chain: List[str], graph: CallGraph) -> Challenge:
    """Generate code tracing challenge"""
    return Challenge(
        type=ChallengeType.CODE_TRACING,
        question={
            'prompt': f"Trace the execution from {chain[0]} to {chain[-1]}",
            'input': generate_sample_input(chain[0], graph),
            'steps': [
                {'step': i+1, 'function': node_id, 'blank': True}
                for i, node_id in enumerate(chain)
            ]
        },
        answer={
            'steps': [
                {'step': i+1, 'function': node_id, 'value': compute_value(node_id)}
                for i, node_id in enumerate(chain)
            ]
        }
    )
```

#### Fill in the Blank Template
```python
def generate_fill_blank(node: CodeNode) -> Challenge:
    """Generate fill-in-blank challenge"""
    # Get actual code
    code = extract_function_code(node)
    
    # Identify key elements to blank out
    blanks = identify_key_elements(code, node)
    
    # Create blanked version
    blanked_code = create_blanks(code, blanks)
    
    return Challenge(
        type=ChallengeType.FILL_BLANK,
        question={
            'code': blanked_code,
            'blanks': len(blanks),
            'hint': f"This function {node.name} {extract_purpose(node.docstring)}"
        },
        answer={
            'fills': blanks
        }
    )
```

### Phase 5: Add Hints & Learning Objectives

**Algorithm**:
```python
def generate_hints(challenge: Challenge, node: CodeNode) -> List[str]:
    """Generate progressive hints"""
    hints = []
    
    # Hint 1: Point to documentation
    if node.docstring:
        hints.append(f"Check the docstring: {node.docstring[:100]}...")
    
    # Hint 2: Reference related code
    if node.calls:
        called = list(node.calls)[0]
        hints.append(f"This function calls {called}")
    
    # Hint 3: Provide code context
    hints.append(f"Look at lines {node.line_start}-{node.line_end}")
    
    return hints


def generate_objectives(chain: List[str], graph: CallGraph) -> List[str]:
    """Generate learning objectives"""
    objectives = []
    
    # Extract patterns
    for node_id in chain:
        node = graph.nodes[node_id]
        
        if node.decorators:
            objectives.append(f"Understand {node.decorators[0]} decorator pattern")
        
        if node.is_async:
            objectives.append("Learn async/await pattern")
        
        if node.complexity > 15:
            objectives.append(f"Master {node.name}'s control flow")
    
    # Add call chain objective
    objectives.insert(0, f"Trace execution from {chain[0]} to {chain[-1]}")
    
    return objectives[:3]  # Max 3 objectives
```

## Complete Level Generation Flow

```python
def generate_levels(call_graph: CallGraph, max_levels: int = 10) -> List[Level]:
    """
    Main entry point for level generation
    
    Args:
        call_graph: Analyzed call graph
        max_levels: Maximum number of levels to generate
    
    Returns:
        List of generated levels
    """
    levels = []
    
    # Phase 1: Identify core chains
    core_chains = identify_core_chains(call_graph)
    
    for i, chain in enumerate(core_chains[:max_levels]):
        # Phase 2: Calculate difficulty
        difficulty = calculate_difficulty(chain, call_graph)
        
        # Phase 3: Select challenge types
        challenge_types = select_challenge_types(chain, difficulty, call_graph)
        
        # Phase 4: Generate challenges
        challenges = []
        for ctype in challenge_types:
            if ctype == ChallengeType.MULTIPLE_CHOICE:
                challenge = generate_multiple_choice(node, call_graph)
            elif ctype == ChallengeType.CODE_TRACING:
                challenge = generate_code_tracing(chain, call_graph)
            # ... other types
            challenges.append(challenge)
        
        # Phase 5: Add metadata
        level = Level(
            id=f"level_{i+1}",
            name=generate_level_name(chain, difficulty),
            description=generate_description(chain, call_graph),
            difficulty=difficulty,
            entry_function=chain[0],
            call_chain=chain,
            code_snippet=extract_relevant_code(chain, call_graph),
            challenges=challenges,
            objectives=generate_objectives(chain, call_graph),
            xp_reward=calculate_xp_reward(difficulty),
            estimated_time=estimate_time(challenges),
            prerequisites=determine_prerequisites(i, levels)
        )
        
        levels.append(level)
    
    return levels
```

## Example Output

### Input: Flask Mini Call Graph
```
Nodes: 15
Entry Points: ['Flask.__call__']
Chains Identified: 5
```

### Output: Generated Levels

**Level 1: WSGI Entry (Tutorial)**
```python
Level(
    name="Understanding Flask's WSGI Interface",
    difficulty=Difficulty.TUTORIAL,
    call_chain=['Flask.__call__', 'Flask.wsgi_app'],
    challenges=[
        MultipleChoice("What protocol does Flask use?"),
        CodeTracing("Trace Flask.__call__ execution"),
        FillBlank("Complete the __call__ method signature")
    ],
    objectives=[
        "Understand WSGI protocol",
        "Learn Flask's entry point"
    ],
    xp_reward=50,
    estimated_time=10
)
```

**Level 2: Request Routing (Basic)**
```python
Level(
    name="Request Routing Mechanism",
    difficulty=Difficulty.BASIC,
    call_chain=['Flask.wsgi_app', 'Flask.full_dispatch_request', 'Map.match'],
    challenges=[
        MultipleChoice("Which component handles URL matching?"),
        CodeTracing("Trace routing flow"),
        FillBlank("Complete the @app.route decorator"),
        CodeCompletion("Implement a simple route handler")
    ],
    objectives=[
        "Trace URL to handler mapping",
        "Understand decorator pattern in routing"
    ],
    xp_reward=100,
    estimated_time=15
)
```

## Quality Metrics

**Generated Level Quality**:
- Diversity: Each level uses 3-5 different challenge types
- Difficulty Progression: +0.5 to +1.5 difficulty per level
- Coverage: Top 5-10 core chains covered
- Time Estimate: 10-30 minutes per level

**Success Criteria**:
- ✅ Generates levels in <5 seconds
- ✅ Difficulty consistently increases
- ✅ Questions are syntactically valid
- ✅ No duplicate questions across levels
- ✅ All prerequisites are satisfied

## Future Enhancements

1. **LLM Integration**: Use GPT-4 for creative question generation
2. **Adaptive Difficulty**: Adjust based on user performance
3. **Community Curation**: Allow humans to review/edit generated levels
4. **Multi-language Support**: Generate questions in user's preferred language
5. **Personalization**: Tailor levels to user's skill level

---

**Status**: Design Complete  
**Next**: Implement in `app/generators/level_generator.py`
