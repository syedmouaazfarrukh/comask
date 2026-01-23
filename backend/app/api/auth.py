"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
import structlog

from app.db.database import get_db
from app.services.auth_service import (
    AuthService,
    UserCreate,
    UserLogin,
    UserResponse,
    TokenPair,
    AuthError,
)
from app.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["authentication"])

# Security scheme
security = HTTPBearer(auto_error=False)


# Cookie settings for httpOnly tokens
COOKIE_SETTINGS = {
    "httponly": True,
    "secure": settings.app_env == "production",  # Only HTTPS in production
    "samesite": "lax",
    "max_age": settings.access_token_expire_minutes * 60,
}

REFRESH_COOKIE_SETTINGS = {
    "httponly": True,
    "secure": settings.app_env == "production",
    "samesite": "lax",
    "max_age": settings.refresh_token_expire_days * 24 * 60 * 60,
    "path": "/auth",  # Only sent to auth endpoints
}


def set_auth_cookies(response: Response, tokens: TokenPair):
    """Set authentication cookies on response."""
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        **COOKIE_SETTINGS
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        **REFRESH_COOKIE_SETTINGS
    )


def clear_auth_cookies(response: Response):
    """Clear authentication cookies."""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token", path="/auth")


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserResponse]:
    """
    Get current authenticated user from token.

    Checks both Authorization header and httpOnly cookie.
    Returns None if not authenticated (for optional auth).
    """
    token = None

    # Check Authorization header first
    if credentials:
        token = credentials.credentials
    # Fall back to cookie
    elif "access_token" in request.cookies:
        token = request.cookies["access_token"]

    if not token:
        return None

    try:
        auth_service = AuthService(db)
        payload = auth_service.verify_token(token)

        if payload.type != "access":
            return None

        user = await auth_service.get_user_by_id(UUID(payload.sub))
        if not user or not user.is_active:
            return None

        return UserResponse.model_validate(user)

    except AuthError:
        return None
    except Exception as e:
        logger.error("Error getting current user", error=str(e))
        return None


async def require_current_user(
    user: Optional[UserResponse] = Depends(get_current_user),
) -> UserResponse:
    """
    Require authenticated user.

    Raises HTTPException if not authenticated.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    Returns user data and sets authentication cookies.
    """
    try:
        auth_service = AuthService(db)
        user, tokens = await auth_service.register(user_data)

        # Set cookies
        set_auth_cookies(response, tokens)

        logger.info("User registered", user_id=str(user.id))
        return UserResponse.model_validate(user)

    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValueError as e:
        # Password validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=TokenPair)
async def login(
    credentials: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password.

    Returns tokens and sets authentication cookies.
    """
    try:
        auth_service = AuthService(db)
        user, tokens = await auth_service.login(credentials)

        # Set cookies
        set_auth_cookies(response, tokens)

        logger.info("User logged in", user_id=str(user.id))
        return tokens

    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token from cookie.
    """
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    try:
        auth_service = AuthService(db)
        tokens = await auth_service.refresh_access_token(refresh_token)

        # Set new cookies
        set_auth_cookies(response, tokens)

        return tokens

    except AuthError as e:
        clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout and revoke refresh token.
    """
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:
        auth_service = AuthService(db)
        await auth_service.logout(refresh_token)

    clear_auth_cookies(response)

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: UserResponse = Depends(require_current_user),
):
    """
    Get current authenticated user.
    """
    return current_user


@router.post("/logout-all")
async def logout_all(
    current_user: UserResponse = Depends(require_current_user),
    response: Response = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Logout from all devices by revoking all refresh tokens.
    """
    auth_service = AuthService(db)
    count = await auth_service.revoke_all_user_tokens(current_user.id)

    clear_auth_cookies(response)

    return {"message": f"Logged out from {count} sessions"}
