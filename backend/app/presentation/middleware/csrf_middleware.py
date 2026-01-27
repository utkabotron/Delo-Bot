"""
CSRF (Cross-Site Request Forgery) protection middleware.

Protects against CSRF attacks on mutation endpoints (POST/PUT/PATCH/DELETE).
Provides backward compatibility with X-Auth-Password authentication.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings
from app.utils.csrf import verify_csrf_token


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware for CSRF protection on mutation endpoints.

    For GET/HEAD/OPTIONS: No CSRF check (safe methods)
    For POST/PUT/PATCH/DELETE:
        1. If X-CSRF-Token header present → verify token
        2. If no token but X-Auth-Password present → allow (backward compat)
        3. Otherwise → reject with 403
    """

    # Safe HTTP methods that don't require CSRF protection
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    # Paths exempt from CSRF check
    EXEMPT_PATHS = [
        "/api/health",
        "/api/csrf-token",  # Endpoint to get new CSRF token
    ]

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods
        if request.method in self.SAFE_METHODS:
            return await call_next(request)

        # Skip CSRF check for exempt paths
        if request.url.path in self.EXEMPT_PATHS:
            return await call_next(request)

        # Skip CSRF check for non-API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        settings = get_settings()

        # Check for CSRF token
        csrf_token = request.headers.get("X-CSRF-Token")

        if csrf_token:
            # CSRF token present - verify it
            if verify_csrf_token(csrf_token, settings.csrf_secret):
                return await call_next(request)
            else:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Invalid or expired CSRF token"}
                )

        # No CSRF token - check for X-Auth-Password (backward compatibility)
        auth_password = request.headers.get("X-Auth-Password")
        if auth_password:
            # Let AuthMiddleware handle password verification
            # If we reached here, password will be checked by AuthMiddleware
            return await call_next(request)

        # No CSRF token and no auth password - reject
        return JSONResponse(
            status_code=403,
            content={"detail": "CSRF token required. Get token from /api/csrf-token endpoint."}
        )
