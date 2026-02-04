# API Endpoint Specifications - Phase 2 Design

## Overview

RESTful API design for the Study with Challenge Game platform. All endpoints follow REST principles and return JSON responses.

**Base URL**: `https://api.studygame.dev/v1`

**Authentication**: OAuth 2.0 + JWT tokens

## Authentication Endpoints

### POST /auth/register
Register a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "username": "code_explorer"
}
```

**Response** (201 Created):
```json
{
  "user_id": "uuid-v4",
  "username": "code_explorer",
  "email": "user@example.com",
  "created_at": "2026-02-03T12:00:00Z"
}
```

### POST /auth/login
Authenticate and get access token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
  "access_token": "jwt-token-here",
  "refresh_token": "refresh-token-here",
  "expires_in": 3600,
  "user": {
    "id": "uuid-v4",
    "username": "code_explorer",
    "level": 5,
    "xp": 12 50
  }
}
```

---

## Project Endpoints

### GET /projects
List all available projects to analyze.

**Query Parameters**:
- `language` (optional): Filter by language (python, golang)
- `difficulty` (optional): Filter by difficulty (1-5)
- `page` (optional): Page number (default: 1)
- `limit` (optional): Results per page (default: 20)

**Response** (200 OK):
```json
{
  "projects": [
    {
      "id": "uuid-v4",
      "name": "Flask",
      "description": "A lightweight WSGI web application framework",
      "language": "python",
      
      "github_url": "https://github.com/pallets/flask",
      "difficulty": 3,
      "total_levels": 10,
      "completed_levels": 0,
      "estimated_time": 120,
      "thumbnail": "https://cdn.studygame.dev/projects/flask.png"
    }
  ],
  "total": 50,
  "page": 1,
  "pages": 3
}
```

### GET /projects/{id}
Get detailed project information.

**Response** (200 OK):
```json
{
  "id": "uuid-v4",
  "name": "Flask",
  "description": "A lightweight WSGI web application framework",
  "language": "python",
  "github_url": "https://github.com/pallets/flask",
  "difficulty": 3,
  "total_levels": 10,
  "estimated_time": 120,
  "levels": [
    {
      "id": "level-1",
      "name": "Understanding WSGI Interface",
      "difficulty": 1,
      "xp_reward": 50,
      "is_unlocked": true,
      "is_completed": false
    },
    {
      "id": "level-2",
      "name": "Request Routing",
      "difficulty": 2,
      "xp_reward": 100,
      "is_unlocked": false,
      "is_completed": false
    }
  ],
  "mini_project": {
    "id": "mini-flask",
    "name": "Build Mini-Flask",
    "is_unlocked": false,
    "xp_reward": 500
  },
  "user_progress": {
    "completed_levels": 0,
    "total_xp_earned": 0,
    "last_played": null
  }
}
```

### POST /projects
Create a new project from GitHub URL (Admin only).

**Request**:
```json
{
  "github_url": "https://github.com/pallets/flask",
  "language": "python",
  "name": "Flask",
  "description": "A lightweight web framework"
}
```

**Response** (202 Accepted):
```json
{
  "project_id": "uuid-v4",
  "status": "analyzing",
  "message": "Project analysis started"
}
```

---

## Analyzer Endpoints

### POST /analyzer/analyze
Trigger analysis of a project (Background job).

**Request**:
```json
{
  "project_id": "uuid-v4",
  "force_reanalyze": false
}
```

**Response** (202 Accepted):
```json
{
  "job_id": "job-uuid",
  "status": "queued",
  "estimated_time": 120
}
```

### GET /analyzer/status/{job_id}
Check analysis job status.

**Response** (200 OK):
```json
{
  "job_id": "job-uuid",
  "status": "completed",
  "progress": 100,
  "result": {
    "nodes_extracted": 150,
    "edges_built": 300,
    "levels_generated": 10,
    "analysis_time": 45.5
  }
}
```

---

## Level Endpoints

### GET /levels/{id}
Get level details with challenges.

**Response** (200 OK):
```json
{
  "id": "level-1",
  "name": "Understanding WSGI Interface",
  "description": "Learn how Flask handles HTTP requests using WSGI",
  "difficulty": 1,
  "entry_function": "Flask.__call__",
  "call_chain": ["Flask.__call__", "Flask.wsgi_app"],
  "code_snippet": "def __call__(self, environ, start_response):\n    ...",
  "objectives": [
    "Understand WSGI protocol",
    "Learn Flask's entry point"
  ],
  "challenges": [
    {
      "id": "challenge-1",
      "type": "multiple_choice",
      "question": {
        "prompt": "What protocol does Flask use for web servers?",
        "options": ["WSGI", "ASGI", "CGI", "FastCGI"]
      },
      "points": 10
    }
  ],
  "xp_reward": 50,
  "estimated_time": 10,
  "prerequisites": [],
  "user_progress": {
    "is_completed": false,
    "attempts": 0,
    "best_score": 0
  }
}
```

### POST /levels/{id}/submit
Submit answers for a level.

**Request**:
```json
{
  "answers": {
    "challenge-1": {"answer": "WSGI"},
    "challenge-2": {"trace": ["Flask.__call__", "Flask.wsgi_app"]},
    "challenge-3": {"code": "return Response(...)"}
  }
}
```

**Response** (200 OK):
```json
{
  "score": 85,
  "max_score": 100,
  "results": {
    "challenge-1": {
      "correct": true,
      "points_earned": 10,
      "feedback": "Correct! WSGI is the Web Server Gateway Interface."
    },
    "challenge-2": {
      "correct": true,
      "points_earned": 15,
      "feedback": "Perfect trace!"
    },
    "challenge-3": {
      "correct": false,
      "points_earned": 0,
      "feedback": "Not quite. Check the return type.",
      "hint": "Flask's __call__ returns a Response object"
    }
  },
  "xp_earned": 50,
  "level_completed": false,
  "passing_score": 70
}
```

---

## Mini Project Endpoints

### GET /mini-projects/{id}
Get mini project details.

**Response** (200 OK):
```json
{
  "id": "mini-flask",
  "name": "Build Mini-Flask",
  "description": "Implement a simplified web framework with core Flask features",
  "difficulty": 4,
  "estimated_time": 90,
  "requirements": [
    "WSGI __call__ interface",
    "Route decorator",
    "URL parameter extraction",
    "Request/Response objects"
  ],
  "starter_code": "class MiniFlask:\n    def __init__(self, name):\n        pass\n    ...",
  "test_cases": [
    {
      "name": "test_basic_route",
      "description": "Test that basic routes work"
    }
  ],
  "xp_reward": 500,
  "is_unlocked": false,
  "user_submission": null
}
```

### POST /mini-projects/{id}/submit
Submit mini project code.

**Request**:
```json
{
  "code": "class MiniFlask:\n    def __init__(self, name):\n        self.name = name\n        self.routes = {}\n    ..."
}
```

**Response** (200 OK):
```json
{
  "submission_id": "sub-uuid",
  "tests_passed": 8,
  "tests_total": 10,
  "score": 82,
  "results": {
    "functional_tests": {
      "passed": 8,
      "total": 10,
      "score": 60
    },
    "code_quality": {
      "score": 16,
      "max": 20,
      "issues": ["Consider adding type hints"]
    },
    "completeness": {
      "score": 6,
      "max": 10,
      "missing": ["Error handling for 500"]
    }
  },
  "reference_unlocked": true,
  "xp_earned": 500,
  "badge_earned": "Framework Architect"
}
```

### GET /mini-projects/{id}/reference
Get reference solution (requires 80%+ score).

**Response** (200 OK):
```json
{
  "code": "class MiniFlask:\n    # Full reference implementation\n    ...",
  "explanation": "This implementation uses regex for URL matching...",
  "key_concepts": [
    "WSGI protocol",
    "Decorator pattern",
    "Regular expressions"
  ]
}
```

**Error Response** (403 Forbidden):
```json
{
  "error": "reference_locked",
  "message": "You must score 80% or higher to unlock the reference solution",
  "current_score": 65,
  "required_score": 80
}
```

---

## User Progress Endpoints

### GET /users/me/progress
Get current user's overall progress.

**Response** (200 OK):
```json
{
  "user_id": "uuid-v4",
  "username": "code_explorer",
  "level": 5,
  "xp": 1250,
  "xp_to_next_level": 250,
  "achievements": [
    {
      "id": "first_level",
      "name": "First Steps",
      "earned_at": "2026-02-01T10:00:00Z"
    }
  ],
  "projects": [
    {
      "project_id": "flask",
      "project_name": "Flask",
      "completed_levels": 3,
      "total_levels": 10,
      "xp_earned": 200,
      "last_played": "2026-02-03T12:00:00Z"
    }
  ],
  "streak": {
    "current": 5,
    "longest": 12,
    "last_activity": "2026-02-03"
  }
}
```

### GET /users/me/stats
Get detailed user statistics.

**Response** (200 OK):
```json
{
  "total_xp": 1250,
  "levels_completed": 15,
  "projects_completed": 1,
  "mini_projects_completed": 1,
  "time_spent_minutes": 420,
  "avg_score": 87.5,
  "challenges_by_type": {
    "multiple_choice": {
      "attempted": 20,
      "correct": 18,
      "accuracy": 90
    },
    "code_tracing": {
      "attempted": 15,
      "correct": 12,
      "accuracy": 80
    }
  },
  "favorite_language": "python"
}
```

---

## Leaderboard Endpoints

### GET /leaderboard
Get global leaderboard.

**Query Parameters**:
- `timeframe` (optional): day, week, month, all-time (default: all-time)
- `language` (optional): Filter by language
- `limit` (optional): Results to return (default: 50)

**Response** (200 OK):
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_id": "uuid",
      "username": "code_master",
      "xp": 5000,
      "level": 25,
      "projects_completed": 5
    }
  ],
  "user_rank": 42,
  "total_users": 1000
}
```

---

## WebSocket API

### WS /ws/live-updates
Real-time updates for user progress.

**Connection**:
```
ws://api.studygame.dev/ws/live-updates?token=jwt-token
```

**Messages Received**:
```json
{
  "type": "xp_earned",
  "data": {
    "amount": 50,
    "source": "level_completed",
    "total_xp": 1300
  }
}

{
  "type": "achievement_unlocked",
  "data": {
    "achievement_id": "speed_demon",
    "name": "Speed Demon",
    "description": "Complete a level in under 5 minutes"
  }
}

{
  "type": "level_unlocked",
  "data": {
    "level_id": "level-4",
    "level_name": "Middleware Pipeline"
  }
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context"
  },
  "timestamp": "2026-02-03T12:00:00Z"
}
```

**Common Error Codes**:
- `401` Unauthorized - Invalid or expired token
- `403` Forbidden - Insufficient permissions
- `404` Not Found - Resource doesn't exist
- `422` Unprocessable Entity - Validation error
- `429` Too Many Requests - Rate limit exceeded
- `500` Internal Server Error - Server issue

---

## Rate Limiting

**Limits**:
- Authentication endpoints: 5 requests/minute
- Analysis endpoints: 10 requests/hour
- Standard endpoints: 100 requests/minute
- WebSocket: 1 connection per user

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1612345678
```

---

## Pagination

All list endpoints support pagination:

**Query Parameters**:
- `page`: Page number (1-indexed)
- `limit`: Items per page (max: 100)

**Response Headers**:
```
X-Total-Count: 500
X-Page: 1
X-Per-Page: 20
X-Total-Pages: 25
Link: </projects?page=2>; rel="next"
```

---

**Status**: API Design Complete  
**Next**: Implement FastAPI routes in `app/api/`
