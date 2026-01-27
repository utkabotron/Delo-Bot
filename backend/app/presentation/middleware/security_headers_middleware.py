"""
Security headers middleware.

Adds security-related HTTP headers to all responses to protect against common attacks.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all HTTP responses.

    Headers added:
    - X-Content-Type-Options: nosniff (prevent MIME sniffing)
    - X-Frame-Options: DENY (prevent clickjacking)
    - X-XSS-Protection: 1; mode=block (enable XSS filter)
    - Content-Security-Policy: restrict content sources
    - Referrer-Policy: no-referrer (don't send referrer header)
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Enable browser XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy
        # Restrict resource loading to same origin, allow inline scripts (Alpine.js, Telegram)
        # Allow CDN for Tailwind and Alpine.js
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://telegram.org https://cdn.tailwindcss.com https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Don't send referrer to external sites
        response.headers["Referrer-Policy"] = "no-referrer"

        # Permissions Policy (formerly Feature-Policy)
        # Disable unused browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
