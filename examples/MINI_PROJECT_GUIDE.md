# Mini Project Implementation Guide

## Overview

Mini Projects are **hidden final challenges** that consolidate learners' understanding by having them implement a simplified version of the framework they just analyzed.

## Design Philosophy

### Learning Loop Closure

```
Understand → Analyze → Practice → Implement
    ↓           ↓          ↓          ↓
  Read      Call Graph  Challenges  Mini Project
```

**Why This Works**:
1. **Active Learning**: Building > passive reading
2. **Pattern Recognition**: Apply learned design patterns
3. **Confidence Building**: "I can build this!"
4. **Portfolio Piece**: Real code to showcase

## Mini Project Structure

### Components

Every mini project includes:

1. **Starter Template** - Code skeleton with TODOs
2. **Requirements** - List of must-have features
3. **Test Suite** - Automated tests to validate
4. **Reference Solution** - Complete implementation (hidden until pass)
5. **Grading Rubric** - Clear scoring criteria

### Example: Mini-Flask

**File**: [`examples/mini_flask.py`](file:///Users/smy/projects/gravity/study_with_challenge_game/examples/mini_flask.py)

**Key Components Implemented**:
```python
class MiniFlask:
    def __init__(self, name):
        # App initialization
    
    def route(self, path):
        # Decorator for URL routing
    
    def match_route(self, path):
        # URL pattern matching with parameters
    
    def __call__(self, environ, start_response):
        # WSGI interface implementation
```

**Core Features**:
- ✅ WSGI `__call__` interface
- ✅ Route decorator (`@app.route()`)
- ✅ URL parameter extraction (`/users/<user_id>`)
- ✅ Request/Response abstraction
- ✅ 404 error handling

**LOC**: ~150 lines (meets target)

**Test Results**:
```
✓ GET / → "Hello, World!"
✓ GET /about → Static route works
✓ GET /users/123 → URL parameters extracted
✓ GET /posts/42/comments/7 → Multiple parameters
✓ GET /unknown → 404 Not Found
```

## Creating a Mini Project

### Step 1: Identify Core Components

From call graph analysis, extract the **essential** components:

**Flask Example**:
```
Full Flask: ~10,000 LOC
Core concepts:
├─ WSGI interface ← ESSENTIAL
├─ Routing ← ESSENTIAL
├─ Request/Response ← ESSENTIAL
├─ Template rendering ← Skip for mini
├─ Session management ← Skip for mini
├─ Blueprint system ← Skip for mini
└─ CLI tools ← Skip for mini

Mini-Flask target: ~150 LOC (98.5% reduction!)
```

### Step 2: Create Starter Template

**Template should have**:
- Class/function skeletons
- Docstrings explaining what to implement
- Type hints (educational value)
- TODO comments

**Example**:
```python
class MiniFlask:
    """Minimal Flask-like web framework
    
    TODO: Implement the following methods:
    - __init__: Initialize app
    - route: Decorator for registering routes
    - __call__: WSGI interface
    """
    
    def __init__(self, name: str):
        """Initialize the application
        
        TODO: Create an empty dict to store routes
        """
        pass  # Your code here
    
    def route(self, path: str):
        """Register a route handler
        
        TODO: Return a decorator that stores the function
        Hint: Use a closure
        """
        pass  # Your code here
```

### Step 3: Write Test Suite

**Test Format** (pytest-style):
```python
def test_basic_route():
    """Test that basic routes work"""
    app = MiniFlask(__name__)
    
    @app.route('/')
    def index():
        return "Hello"
    
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
    response = mock_request(app, environ)
    
    assert response.status == 200
    assert response.data == "Hello"

def test_url_parameters():
    """Test URL parameter extraction"""
    app = MiniFlask(__name__)
    
    @app.route('/users/<user_id>')
    def get_user(user_id):
        return f"User: {user_id}"
    
    environ = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/123'}
    response = mock_request(app, environ)
    
    assert response.status == 200
    assert "123" in response.data
```

**Test Categories**:
- **Functional** (60%): Core features work
- **Edge Cases** (20%): Error handling, 404s, etc.
- **Code Quality** (20%): Follows patterns, proper structure

### Step 4: Reference Solution

**How we provide it**:
1. User completes implementation
2. Submits for testing
3. **Must pass 80%+ tests** to unlock reference
4. Side-by-side comparison shown
5. Highlight differences

**Educational Value**:
- See alternative implementations
- Learn edge cases they missed
- Understand trade-offs

## Integration with Platform

### Database Schema

```sql
-- Store mini project metadata
CREATE TABLE mini_projects (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    starter_code TEXT,  -- Template with TODOs
    reference_solution TEXT,  -- Our implementation
    test_cases JSONB,  -- Test suite
    xp_reward INTEGER DEFAULT 500
);

-- Track user submissions
CREATE TABLE mini_project_submissions (
    id UUID PRIMARY KEY,
    user_id UUID,
    mini_project_id UUID,
    code TEXT,  -- User's implementation
    tests_passed INTEGER,
    tests_total INTEGER,
    score INTEGER,
    status VARCHAR(50)  -- in_progress/submitted/passed
);
```

### API Endpoints

```
POST /api/v1/mini-projects/{id}/submit
  Body: { "code": "class MiniFlask:..." }
  → Run tests
  → Return { "tests_passed": 5, "tests_total": 5, "score": 100 }

GET /api/v1/mini-projects/{id}/reference
  Requires: tests_passed >= 80%
  → Return reference solution

POST /api/v1/mini-projects/{id}/compare
  Body: { "code": "user code" }
  → Return side-by-side diff
```

### UI Flow

```
1. User completes all levels ✓
2. 🎯 "Hidden Challenge Unlocked!" notification
3. Click → Opens Mini Project page
4. Shows:
   - Description
   - Requirements
   - Starter template in Monaco Editor
   - "Run Tests" button
5. User codes → Clicks "Run Tests"
6. Results shown:
   ✓ test_basic_route PASSED
   ✓ test_url_parameters PASSED
   ✗ test_404_handling FAILED
   Score: 67% (4/6 tests)
7. Fix code → Re-run
8. All tests pass → "Submit" button enabled
9. Submit → Reference solution unlocked
10. View comparison → Learn improvements
11. Earn badge + XP + Certificate
```

## Mini Project Examples

### 1. Mini-Flask (Web Framework)

**Difficulty**: Medium  
**LOC Target**: 150  
**Time**: 60-90 minutes

**Core Concepts**:
- WSGI interface
- Decorator pattern
- URL routing with regex
- Request/Response abstraction

**Implementation**: [examples/mini_flask.py](file:///Users/smy/projects/gravity/study_with_challenge_game/examples/mini_flask.py)

### 2. Mini-Requests (HTTP Client)

**Difficulty**: Medium  
**LOC Target**: 100  
**Time**: 45-60 minutes

**Core Concepts**:
- HTTP protocol basics
- Connection pooling (simplified)
- Response parsing
- JSON handling

**Key Classes**:
```python
class Response:
    - status_code
    - text
    - json()

class Session:
    - get(url)
    - post(url, data)
    - _connection_pool
```

### 3. Mini-Click (CLI Framework)

**Difficulty**: Easy  
**LOC Target**: 80  
**Time**: 30-45 minutes

**Core Concepts**:
- Decorator pattern
- Argument parsing
- Command groups

**Key Features**:
- `@click.command()` decorator
- `@click.option()` for flags
- Help text generation

### 4. Mini-SQLAlchemy (ORM)

**Difficulty**: Hard  
**LOC Target**: 200  
**Time**: 90-120 minutes

**Core Concepts**:
- Metaclasses
- Descriptor protocol
- Query building
- Database abstraction

**Key Classes**:
```python
class Model(metaclass=ModelMeta):
    - save()
    - delete()

class Column:
    - __get__/__set__ (descriptor)

class Query:
    - filter()
    - all()
    - first()
```

## Best Practices

### DO ✓

- ✅ Keep it **focused** (100-200 LOC max)
- ✅ Use **clear naming** (educational code)
- ✅ Include **docstrings** explaining design
- ✅ Provide **comprehensive tests**
- ✅ Match **framework's patterns**
- ✅ Add **inline comments** for tricky parts

### DON'T ✗

- ❌ Include production features (logging, monitoring)
- ❌ Add unnecessary complexity
- ❌ Make it too easy (copy-paste from reference)
- ❌ Make it too hard (frustrating)
- ❌ Skip error handling entirely
- ❌ Ignore code quality

## Grading Rubric Template

```python
# Automatic grading based on test results and code analysis

GRADING = {
    "functional_tests": {
        "weight": 0.60,
        "criteria": "All required tests pass"
    },
    "code_quality": {
        "weight": 0.20,
        "criteria": [
            "Proper class structure",
            "Meaningful variable names",
            "Docstrings present",
            "No code duplication"
        ]
    },
    "completeness": {
        "weight": 0.10,
        "criteria": "All required components implemented"
    },
    "bonus": {
        "weight": 0.10,
        "criteria": [
            "Extra features (+5%)",
            "Exceptional code quality (+3%)",
            "Creative solution (+2%)"
        ]
    }
}
```

## Content Creation Workflow

For each framework we want to support:

1. **Analyze framework** (already done in levels)
2. **Identify 3-5 core components** to implement
3. **Write reference solution** (100-200 LOC)
4. **Extract starter template** (remove implementation)
5. **Write test suite** (10-15 tests)
6. **Create requirements checklist**
7. **Manual QA** (test with real users)
8. **Iterate** based on feedback

## Metrics to Track

**Engagement**:
- % of users who attempt mini project
- Avg time to complete
- Completion rate

**Learning**:
- Avg tests passed on first attempt
- Common errors (inform hints)
- Comparison with reference (diff analysis)

**Satisfaction**:
- User ratings
- "Would recommend" score
- Badge display rate

## Future Enhancements

### Phase 2+:
- **Multiple solutions**: Show 3 different approaches
- **Code review AI**: GPT-4 feedback on user code
- **Community submissions**: Users vote on best implementations
- **Video walkthroughs**: Recorded explanations
- **Pair programming mode**: Collaborate with others

---

**Next Steps**: Create mini projects for these frameworks (in order):
1. ✅ Mini-Flask (Done)
2. Mini-Requests
3. Mini-Click
4. Mini-Pytest
5. Mini-SQLAlchemy
