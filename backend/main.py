"""
Indian Election Process Education Assistant — FastAPI Application Entry Point.

This is the main application module that:
  - Creates the FastAPI app with OpenAPI documentation
  - Registers all API routers
  - Configures CORS, rate limiting, and middleware
  - Provides health check endpoint
  - Handles global exceptions

Cloud Run compatible: stateless, PORT from environment, no sticky sessions.
"""

import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi.errors import RateLimitExceeded
from core.config import settings
from core.middleware import configure_middleware
from models.common import HealthResponse, ErrorResponse

# --- Configure structured logging for Cloud Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


# --- Create FastAPI Application ---
app = FastAPI(
    title="Indian Election Process Education Assistant",
    description=(
        "A stateless, cloud-native API that guides voters through India's "
        "electoral framework. Provides deterministic registration guidance, "
        "localized polling timelines, and AI-powered FAQ resolution grounded "
        "in verified ECI (Election Commission of India) documents."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# --- CORS Configuration (plan.md: Security Model Section 2) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept"],
    max_age=3600,
)


# --- Apply middleware (rate limiting, request logging) ---
configure_middleware(app)


# --- Register API Routers ---
from api.eligibility import router as eligibility_router
from api.timeline import router as timeline_router
from api.guide import router as guide_router
from api.faq import router as faq_router

app.include_router(eligibility_router)
app.include_router(timeline_router)
app.include_router(guide_router)
app.include_router(faq_router)


# --- Health Check Endpoint (required for Cloud Run) ---
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
    description="Returns the health status of the service. "
    "Used by Cloud Run for readiness and liveness probes.",
)
async def health_check() -> HealthResponse:
    """Service health check endpoint."""
    return HealthResponse(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version="1.0.0",
    )


@app.get(
    "/",
    tags=["System"],
    summary="API root",
    description="Returns basic API information and links to documentation.",
)
async def root():
    """API root — returns service info."""
    return {
        "service": "Indian Election Process Education Assistant",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "eligibility": "POST /api/v1/eligibility/evaluate",
            "guide": "GET /api/v1/guide/next-step",
            "timeline": "GET /api/v1/timeline",
            "faq": "POST /api/v1/faq/ask",
        },
    }


# --- Global Exception Handlers ---
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Return 429 when rate limit is exceeded."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": "60s"
        },
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "not_found",
            "message": f"The requested resource '{request.url.path}' was not found.",
        },
    )

@app.exception_handler(422)
@app.exception_handler(ValueError)
async def validation_error_handler(request: Request, exc):
    """Custom validation error handler with user-friendly messages."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": "Invalid request data. Please check your input and try again.",
            "details": str(exc)
        },
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler — logs error, returns safe message."""
    logger.exception("Internal server error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# --- Startup / Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    """Application startup — log configuration."""
    logger.info("=" * 60)
    logger.info("Indian Election Process Education Assistant starting...")
    logger.info("Environment: %s", settings.ENVIRONMENT)
    logger.info("GCP Project: %s", settings.GCP_PROJECT_ID)
    logger.info("GCP Location: %s", settings.GCP_LOCATION)
    logger.info("CORS Origins: %s", settings.CORS_ORIGINS)
    logger.info("LLM Model: %s", settings.VERTEX_LLM_MODEL)
    logger.info("Embedding Model: %s", settings.VERTEX_EMBEDDING_MODEL)
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown — cleanup."""
    logger.info("Application shutting down.")
