"""
Basic API integration tests
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models.user import User


client = TestClient(app)


@pytest.fixture
def test_db():
    """Provide a test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Study with Challenge API"
    assert data["version"] == "1.0.0"


def test_user_registration():
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "test1234"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@test.com"
    assert "id" in data
    assert "hashed_password" not in data


def test_user_login():
    """Test user login"""
    # First register a user
    client.post(
        "/auth/register",
        json={
            "username": "logintest",
            "email": "login@test.com",
            "password": "test1234"
        }
    )
    
    # Then login
    response  = client.post(
        "/auth/login",
        json={
            "email": "login@test.com",
            "password": "test1234"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data


def test_get_current_user():
    """Test getting current user info"""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "username": "authtest",
            "email": "auth@test.com",
            "password": "test1234"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "auth@test.com",
            "password": "test1234"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get user info
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "authtest"
    assert data["email"] == "auth@test.com"


def test_list_projects():
    """Test listing projects"""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "username": "projecttest",
            "email": "project@test.com",
            "password": "test1234"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "project@test.com",
            "password": "test1234"
        }
    )
    token = login_response.json()["access_token"]
    
    # List projects
    response = client.get(
        "/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data


def test_user_stats():
    """Test getting user stats"""
    # Register and login
    client.post(
        "/auth/register",
        json={
            "username": "statstest",
            "email": "stats@test.com",
            "password": "test1234"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "stats@test.com",
            "password": "test1234"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get stats
    response = client.get(
        "/users/me/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_xp" in data
    assert "current_level" in data
    assert "levels_completed" in data
    assert data["total_xp"] == 0  # New user
    assert data["current_level"] == 1
