"""
Shared response models used across multiple API endpoints.
"""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response envelope."""
    error: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")


class HealthResponse(BaseModel):
    """Health check endpoint response."""
    status: str = Field(default="healthy", description="Service health status")
    environment: str = Field(..., description="Current deployment environment")
    version: str = Field(default="1.0.0", description="API version")
