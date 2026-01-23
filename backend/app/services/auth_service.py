"""Authentication service with JWT and bcrypt."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from uuid import UUID
import secrets
import hashlib

from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, EmailStr, field_validator
import structlog

from app.config import settings
from app.db.models import User, RefreshToken

logger = structlog.get_logger()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Pydantic models for auth
class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < settings.password_min_length:
            raise ValueError(f"Password must be at least {settings.password_min_length} characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)."""
    id: UUID
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenPair(BaseModel):
    """Schema for JWT token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenPayload(BaseModel):
    """Schema for decoded JWT payload."""
    sub: str  # user_id
    exp: datetime
    type: str  # "access" or "refresh"


class AuthError(Exception):
    """Authentication error."""
    pass


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # Password operations

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    # Token operations

    @staticmethod
    def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.access_token_expire_minutes)

        expire = datetime.now(timezone.utc) + expires_delta
        payload = {
            "sub": user_id,
            "exp": expire,
            "type": "access",
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def create_refresh_token() -> str:
        """Create a secure refresh token."""
        return secrets.token_urlsafe(64)

    @staticmethod
    def hash_refresh_token(token: str) -> str:
        """Hash a refresh token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def verify_token(token: str) -> TokenPayload:
        """
        Verify and decode a JWT token.

        Raises:
            AuthError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return TokenPayload(**payload)
        except JWTError as e:
            logger.warning("JWT verification failed", error=str(e))
            raise AuthError("Invalid or expired token")

    # User operations

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.

        Raises:
            AuthError: If email already exists
        """
        # Check if email already exists
        existing = await self.get_user_by_email(user_data.email)
        if existing:
            raise AuthError("Email already registered")

        # Create user
        user = User(
            email=user_data.email.lower(),
            password_hash=self.hash_password(user_data.password),
            full_name=user_data.full_name,
            is_active=True,
            is_verified=False,  # Would be True after email verification
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        logger.info("User created", user_id=str(user.id), email=user.email)
        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email and password.

        Returns:
            User if authentication successful, None otherwise
        """
        user = await self.get_user_by_email(email)
        if not user:
            # Use same timing as password check to prevent timing attacks
            self.hash_password("dummy_password")
            return None

        if not self.verify_password(password, user.password_hash):
            return None

        if not user.is_active:
            return None

        return user

    # Token pair operations

    async def create_token_pair(self, user: User) -> TokenPair:
        """Create access and refresh token pair for a user."""
        # Create tokens
        access_token = self.create_access_token(str(user.id))
        refresh_token = self.create_refresh_token()

        # Store refresh token hash in database
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=self.hash_refresh_token(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        )
        self.db.add(refresh_token_record)

        # Update last login
        user.last_login = datetime.now(timezone.utc)

        await self.db.flush()

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenPair:
        """
        Refresh an access token using a refresh token.

        Raises:
            AuthError: If refresh token is invalid or expired
        """
        token_hash = self.hash_refresh_token(refresh_token)

        # Find the refresh token in database
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.revoked == False,
                    RefreshToken.expires_at > datetime.now(timezone.utc),
                )
            )
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise AuthError("Invalid or expired refresh token")

        # Revoke old refresh token (rotation)
        token_record.revoked = True
        token_record.revoked_at = datetime.now(timezone.utc)

        # Get user
        user = await self.get_user_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise AuthError("User not found or inactive")

        # Create new token pair
        return await self.create_token_pair(user)

    async def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        Revoke a refresh token (logout).

        Returns:
            True if token was revoked, False if not found
        """
        token_hash = self.hash_refresh_token(refresh_token)

        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token_hash == token_hash,
                    RefreshToken.revoked == False,
                )
            )
        )
        token_record = result.scalar_one_or_none()

        if token_record:
            token_record.revoked = True
            token_record.revoked_at = datetime.now(timezone.utc)
            return True

        return False

    async def revoke_all_user_tokens(self, user_id: UUID) -> int:
        """
        Revoke all refresh tokens for a user.

        Returns:
            Number of tokens revoked
        """
        result = await self.db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked == False,
                )
            )
        )
        tokens = result.scalars().all()

        now = datetime.now(timezone.utc)
        for token in tokens:
            token.revoked = True
            token.revoked_at = now

        return len(tokens)

    # Login/Register flow

    async def register(self, user_data: UserCreate) -> Tuple[User, TokenPair]:
        """
        Register a new user and return tokens.

        Returns:
            Tuple of (user, token_pair)
        """
        user = await self.create_user(user_data)
        tokens = await self.create_token_pair(user)
        return user, tokens

    async def login(self, credentials: UserLogin) -> Tuple[User, TokenPair]:
        """
        Login a user and return tokens.

        Raises:
            AuthError: If credentials are invalid
        """
        user = await self.authenticate_user(credentials.email, credentials.password)
        if not user:
            raise AuthError("Invalid email or password")

        tokens = await self.create_token_pair(user)
        return user, tokens

    async def logout(self, refresh_token: str) -> bool:
        """
        Logout by revoking refresh token.

        Returns:
            True if successful
        """
        return await self.revoke_refresh_token(refresh_token)


# Dependency for getting auth service
async def get_auth_service(db: AsyncSession) -> AuthService:
    """Dependency for getting auth service instance."""
    return AuthService(db)
