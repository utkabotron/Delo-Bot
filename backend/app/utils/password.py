"""
Password hashing and verification utilities using bcrypt.

Provides backward compatibility: can verify both plain text and hashed passwords.
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password as a string (bcrypt format: $2b$...)
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password

    Returns:
        True if password matches, False otherwise
    """
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    try:
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except (ValueError, Exception):
        # If hash is invalid format, return False
        return False


def is_hashed(password: str) -> bool:
    """
    Check if a password is already hashed with bcrypt.

    Bcrypt hashes always start with '$2a$', '$2b$', or '$2y$'.

    Args:
        password: Password string to check

    Returns:
        True if password is bcrypt-hashed, False if plain text
    """
    return password.startswith(('$2a$', '$2b$', '$2y$'))
