"""Authentication middleware for request processing."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable, List, Optional
import structlog

from app.services.auth_service import AuthService
from app.config import settings

logger = structlog.get_logger()


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate authentication from requests.

    This middleware:
    1. Extracts token from Authorization header or cookie
    2. Validates the token
    3. Attaches user info to request.state for downstream handlers
    """

    # Paths that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/auth/login",
        "/auth/register",
        "/auth/refresh",
    ]

    # Path prefixes that don't require authentication
    PUBLIC_PREFIXES = [
        "/auth/",
        "/api/queries",
        "/api/conversations",
        "/api/data",
    ]

    def __init__(self, app, exclude_paths: Optional[List[str]] = None):
        """
        Initialize auth middleware.

        Args:
            app: ASGI application
            exclude_paths: Additional paths to exclude from auth
        """
        super().__init__(app)
        self.exclude_paths = set(self.PUBLIC_PATHS)
        if exclude_paths:
            self.exclude_paths.update(exclude_paths)

    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require auth)."""
        if path in self.exclude_paths:
            return True

        for prefix in self.PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True

        return False

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and attach user info if authenticated."""

        # Skip auth for public paths
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # Extract token
        token = self._extract_token(request)

        if token:
            try:
                # Validate token and extract user info
                payload = AuthService.verify_token(token)

                # Attach to request state for downstream handlers
                request.state.user_id = payload.sub
                request.state.token_type = payload.type
                request.state.authenticated = True

            except Exception as e:
                logger.debug("Auth token validation failed", error=str(e))
                request.state.authenticated = False
                request.state.user_id = None
        else:
            request.state.authenticated = False
            request.state.user_id = None

        return await call_next(request)

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract authentication token from request."""

        # Check Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]

        # Fall back to cookie
        return request.cookies.get("access_token")
