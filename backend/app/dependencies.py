"""
FastAPI dependencies for authentication and database
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.core.security import decode_access_token
from app.core.exceptions import CredentialsException, UserNotFoundException
from app.models.user import User


# HTTP Bearer security scheme
security = HTTPBearer()


def get_db() -> Generator[Session, None, None]:
    """
    Get database session
    
    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Usage:
        @app.get("/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    
    Raises:
        CredentialsException: If token is invalid
        UserNotFoundException: If user not found
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise CredentialsException()
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise CredentialsException()
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UserNotFoundException()
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (convenience dependency)"""
    return current_user
