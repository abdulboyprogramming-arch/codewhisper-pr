# ============================================================
# CodeWhisper PR - Custom Exceptions
# ============================================================

from typing import Optional, Any


class CodeWhisperError(Exception):
    """Base exception for CodeWhisper PR."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class AuthenticationError(CodeWhisperError):
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(CodeWhisperError):
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(message, status_code=403, details=details)


class DatabaseError(CodeWhisperError):
    def __init__(self, message: str = "Database operation failed", details: Optional[Any] = None):
        super().__init__(message, status_code=500, details=details)


class GitError(CodeWhisperError):
    def __init__(self, message: str = "Git operation failed", details: Optional[Any] = None):
        super().__init__(message, status_code=500, details=details)


class ParitokError(CodeWhisperError):
    def __init__(self, message: str = "Paritok operation failed", details: Optional[Any] = None):
        super().__init__(message, status_code=500, details=details)


class LLMError(CodeWhisperError):
    def __init__(self, message: str = "LLM operation failed", details: Optional[Any] = None):
        super().__init__(message, status_code=500, details=details)


class ReviewError(CodeWhisperError):
    def __init__(self, message: str = "Review process failed", details: Optional[Any] = None):
        super().__init__(message, status_code=500, details=details)


class ValidationError(CodeWhisperError):
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(message, status_code=400, details=details)


class RateLimitError(CodeWhisperError):
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Any] = None):
        super().__init__(message, status_code=429, details=details)
