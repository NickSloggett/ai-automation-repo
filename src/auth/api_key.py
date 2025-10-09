"""API key authentication and management."""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..database.models import APIKey

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_api_key() -> str:
    """Generate a secure random API key.

    Returns:
        Secure random API key string
    """
    return f"ak_{secrets.token_urlsafe(32)}"


async def create_api_key(
    db: AsyncSession,
    user_id: str,
    name: str,
    scopes: list[str] = None,
    expires_in_days: Optional[int] = None,
) -> APIKey:
    """Create a new API key for a user.

    Args:
        db: Database session
        user_id: User ID
        name: API key name/description
        scopes: Permission scopes
        expires_in_days: Days until expiration (None = never expires)

    Returns:
        Created API key
    """
    key_value = generate_api_key()

    expires_at = None
    if expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

    api_key = APIKey(
        key=key_value,
        user_id=user_id,
        name=name,
        scopes=scopes or [],
        expires_at=expires_at,
        is_active=True,
    )

    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return api_key


async def validate_api_key(
    db: AsyncSession,
    api_key: str,
) -> Optional[APIKey]:
    """Validate an API key.

    Args:
        db: Database session
        api_key: API key to validate

    Returns:
        API key object if valid, None otherwise
    """
    result = await db.execute(
        select(APIKey).where(
            APIKey.key == api_key,
            APIKey.is_active == True,
        )
    )

    key_obj = result.scalar_one_or_none()

    if not key_obj:
        return None

    # Check expiration
    if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
        return None

    # Update last used timestamp
    key_obj.last_used_at = datetime.utcnow()
    key_obj.usage_count += 1
    await db.commit()

    return key_obj


async def revoke_api_key(
    db: AsyncSession,
    api_key_id: str,
    user_id: str,
) -> bool:
    """Revoke an API key.

    Args:
        db: Database session
        api_key_id: API key ID to revoke
        user_id: User ID (for authorization)

    Returns:
        True if revoked, False if not found
    """
    result = await db.execute(
        select(APIKey).where(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id,
        )
    )

    key_obj = result.scalar_one_or_none()

    if not key_obj:
        return False

    key_obj.is_active = False
    key_obj.revoked_at = datetime.utcnow()
    await db.commit()

    return True


async def get_api_key_user(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """Dependency to get user from API key.

    Args:
        api_key: API key from header
        db: Database session

    Returns:
        API key object

    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
        )

    key_obj = await validate_api_key(db, api_key)

    if not key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key",
        )

    return key_obj


def require_api_scope(required_scope: str):
    """Dependency to require specific API scope.

    Args:
        required_scope: Required permission scope

    Returns:
        Dependency function
    """

    async def scope_checker(api_key: APIKey = Depends(get_api_key_user)):
        if required_scope not in api_key.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key does not have required scope: {required_scope}",
            )
        return api_key

    return scope_checker





