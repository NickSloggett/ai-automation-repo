"""Authentication models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class User(BaseModel):
    """User model for authentication."""

    id: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    scopes: list[str] = []


class TokenData(BaseModel):
    """JWT token data."""

    user_id: str
    email: str
    scopes: list[str] = []
    exp: Optional[datetime] = None


class APIKey(BaseModel):
    """API key model."""

    id: str
    key: str
    user_id: str
    name: str
    scopes: list[str]
    is_active: bool
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0
    created_at: datetime


class LoginRequest(BaseModel):
    """Login request model."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response model."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class CreateAPIKeyRequest(BaseModel):
    """Create API key request."""

    name: str
    scopes: list[str] = []
    expires_in_days: Optional[int] = None


class CreateAPIKeyResponse(BaseModel):
    """Create API key response."""

    api_key: str
    name: str
    scopes: list[str]
    expires_at: Optional[datetime]
    message: str = "Store this API key securely. It won't be shown again."





