"""
Custom application exceptions.

Provides structured exception hierarchy for better error handling.
"""


class DelocatorException(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(DelocatorException):
    """Raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationException(DelocatorException):
    """Raised when validation fails."""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=400)


class AuthenticationException(DelocatorException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class PermissionException(DelocatorException):
    """Raised when user doesn't have permission."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class ExternalServiceException(DelocatorException):
    """Raised when external service (Google Sheets, etc.) fails."""

    def __init__(self, message: str = "External service error", status_code: int = 502):
        super().__init__(message, status_code=status_code)
