# Backend API

FastAPI backend for Study with Challenge game platform.

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY
```

### 3. Populate Sample Data

```bash
python3 scripts/populate_data.py
```

This creates:
- 2 users: `admin/admin123`, `testuser/test123`
- 1 sample project (Mini-Flask)
- 2 levels with challenges
- 3 achievements

### 4. Run Server

```bash
python3 -m uvicorn app.main:app --reload --port 8000
```

Server runs at: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - Login (returns JWT)
- `GET /auth/me` - Get current user

### Projects
- `GET /projects` - List projects (filters: language, difficulty)
- `GET /projects/{id}` - Get project details
- `POST /projects` - Create project (admin only)

### Levels
- `GET /levels/{id}` - Get level with challenges
- `POST /levels/{id}/submit` - Submit answers

### Users
- `GET /users/me/stats` - User statistics
- `GET /users/me/progress` - All projects progress
- `GET /users/me/progress/{project_id}` - Detailed progress
- `GET /users/me/achievements` - Achievements list

## Testing

### Run Tests

```bash
pytest tests/ -v
```

### Manual Testing

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | python3 -c "import json, sys; print(json.load(sys.stdin)['access_token'])")

# Get projects
curl -s http://localhost:8000/projects \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get user stats
curl -s http://localhost:8000/users/me/stats \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

## Database

- **Development**: SQLite (`study_game.db`)
- **Production**: PostgreSQL (change `DATABASE_URL` in `.env`)

### Reset Database

```bash
rm -f study_game.db
python3 scripts/populate_data.py
```

## Architecture

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **JWT** - Authentication
- **Bcrypt** - Password hashing

## Project Structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app
│   ├── config.py        # Settings
│   ├── database.py      # SQLAlchemy setup
│   ├── dependencies.py  # Auth dependencies
│   ├── api/            # API routes
│   │   ├── auth.py
│   │   ├── projects.py
│   │   ├── levels.py
│   │   └── users.py
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   └── core/           # Security, exceptions
├── scripts/
│   └── populate_data.py
├── tests/
│   └── test_api.py
└── requirements.txt
```

## Environment Variables

```env
DATABASE_URL=sqlite:///./study_game.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:5173
```

## Development

1. Make changes to code
2. Server auto-reloads (uvicorn --reload)
3. Test with Swagger UI at `/docs`
4. Run tests with `pytest`

## Production Deployment

1. Set `DATABASE_URL` to PostgreSQL
2. Generate strong `SECRET_KEY`
3. Set `CORS_ORIGINS` to production domain
4. Use gunicorn/uvicorn workers
5. Setup reverse proxy (nginx)
