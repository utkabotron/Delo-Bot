"""
CSRF (Cross-Site Request Forgery) protection utilities.

Simplified CSRF protection without sessions:
- Tokens are stateless (JWT-style) with expiration
- Signed with app secret to prevent tampering
"""

import secrets
import hashlib
import time
from typing import Optional


# Token lifetime in seconds (1 hour)
TOKEN_LIFETIME = 3600


def generate_csrf_token(secret: str) -> str:
    """
    Generate a new CSRF token.

    Format: {timestamp}.{random}.{signature}

    Args:
        secret: Application secret for signing

    Returns:
        CSRF token string
    """
    timestamp = str(int(time.time()))
    random_part = secrets.token_urlsafe(16)
    message = f"{timestamp}.{random_part}"
    signature = _sign(message, secret)

    return f"{message}.{signature}"


def verify_csrf_token(token: str, secret: str) -> bool:
    """
    Verify a CSRF token.

    Args:
        token: CSRF token to verify
        secret: Application secret for verification

    Returns:
        True if token is valid and not expired, False otherwise
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return False

        timestamp_str, random_part, signature = parts
        timestamp = int(timestamp_str)

        # Check expiration
        current_time = int(time.time())
        if current_time - timestamp > TOKEN_LIFETIME:
            return False

        # Verify signature
        message = f"{timestamp_str}.{random_part}"
        expected_signature = _sign(message, secret)

        return secrets.compare_digest(signature, expected_signature)

    except (ValueError, Exception):
        return False


def _sign(message: str, secret: str) -> str:
    """
    Sign a message with HMAC-SHA256.

    Args:
        message: Message to sign
        secret: Secret key

    Returns:
        Hex-encoded signature
    """
    combined = f"{message}{secret}".encode("utf-8")
    return hashlib.sha256(combined).hexdigest()[:16]  # Use first 16 chars for brevity
