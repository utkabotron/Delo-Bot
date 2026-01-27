"""
Security-related API endpoints.
"""

from fastapi import APIRouter
from app.config import get_settings
from app.utils.csrf import generate_csrf_token

router = APIRouter(prefix="/api", tags=["security"])


@router.get("/csrf-token")
def get_csrf_token():
    """
    Get a new CSRF token for making mutation requests.

    The token should be sent in X-CSRF-Token header for POST/PUT/PATCH/DELETE requests.
    Token is valid for 1 hour.

    Returns:
        Dict with CSRF token
    """
    settings = get_settings()
    token = generate_csrf_token(settings.csrf_secret)

    return {"csrf_token": token}
