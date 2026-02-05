"""
Custom HTTP exceptions
"""
from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    """Exception for invalid credentials"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundException(HTTPException):
    """Exception for user not found"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )


class ProjectNotFoundException(HTTPException):
    """Exception for project not found"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )


class LevelNotFoundException(HTTPException):
    """Exception for level not found"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Level not found"
        )


class UserAlreadyExistsException(HTTPException):
    """Exception for duplicate user registration"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
