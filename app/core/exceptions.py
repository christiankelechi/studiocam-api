"""Custom Domain Exceptions for StudioCam AI."""

from typing import Any, Optional


class StudioException(Exception):
    """Base exception for all StudioCam domain errors."""

    def __init__(self, message: str, status_code: int = 400, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class AuthenticationError(StudioException):
    """Raised when authentication fails or token is invalid."""

    def __init__(self, message: str = "Invalid credentials or expired session", details: Optional[Any] = None):
        super().__init__(message=message, status_code=401, details=details)


class PermissionDeniedError(StudioException):
    """Raised when user lacks permission to access resource."""

    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(message=message, status_code=403, details=details)


class ResourceNotFoundError(StudioException):
    """Raised when requested project, asset, or entity does not exist."""

    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} with ID '{resource_id}' was not found"
        super().__init__(message=message, status_code=404, details={"resource": resource, "id": resource_id})


class InsufficientCreditsError(StudioException):
    """Raised when user lacks credits for an AI generation operation."""

    def __init__(self, required: int, available: int):
        message = f"Insufficient credits: {required} required, {available} available"
        super().__init__(message=message, status_code=402, details={"required": required, "available": available})


class AIPipelineError(StudioException):
    """Raised when an AI model engine fails to process image or video."""

    def __init__(self, engine_name: str, reason: str):
        message = f"AI Engine '{engine_name}' processing failed: {reason}"
        super().__init__(message=message, status_code=500, details={"engine": engine_name, "reason": reason})

