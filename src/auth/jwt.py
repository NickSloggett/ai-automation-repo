"""JWT authentication implementation."""

from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from ..config import get_settings

settings = get_settings()
security = HTTPBearer()


class TokenData(BaseModel):
    """JWT token data."""

    user_id: str
    email: str
    scopes: list[str] = []
    exp: Optional[datetime] = None


def create_access_token(
    user_id: str,
    email: str,
    scopes: list[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token.

    Args:
        user_id: User ID
        email: User email
        scopes: Permission scopes
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(hours=24)

    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": user_id,
        "email": email,
        "scopes": scopes or [],
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.secret_key,
        algorithm=settings.auth.algorithm,
    )

    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decode and validate JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.auth.secret_key,
            algorithms=[settings.auth.algorithm],
        )

        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        scopes: list[str] = payload.get("scopes", [])
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(user_id=user_id, email=email, scopes=scopes, exp=exp)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """Get current authenticated user from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        Token data with user information

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    return decode_access_token(token)


def require_scope(required_scope: str):
    """Dependency to require specific scope.

    Args:
        required_scope: Required permission scope

    Returns:
        Dependency function
    """

    async def scope_checker(token_data: TokenData = Depends(get_current_user)):
        if required_scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required scope: {required_scope}",
            )
        return token_data

    return scope_checker





