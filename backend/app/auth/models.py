"""Auth-related Pydantic models."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=2, max_length=100)


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User info response."""
    id: int
    email: str
    display_name: str
    role: str
    created_at: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Password change request."""
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """User profile update."""
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
