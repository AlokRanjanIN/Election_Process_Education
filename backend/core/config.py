"""
Application configuration loaded from environment variables.
Cloud Run injects these at runtime via Secret Manager or Console.
"""

import os
from typing import List


class Settings:
    """Immutable application settings sourced from environment variables."""

    # --- Google Cloud Platform ---
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "election-platform-dev")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION", "asia-south1")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # --- CORS ---
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
        ).split(",")
    ]

    # --- Vertex AI Model Configuration ---
    VERTEX_LLM_MODEL: str = os.getenv("VERTEX_LLM_MODEL", "gemini-1.5-flash-001")
    VERTEX_EMBEDDING_MODEL: str = os.getenv(
        "VERTEX_EMBEDDING_MODEL", "text-embedding-004"
    )
    VERTEX_LLM_TEMPERATURE: float = float(
        os.getenv("VERTEX_LLM_TEMPERATURE", "0.0")
    )

    # --- RAG Pipeline ---
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    RAG_MAX_QUERY_LENGTH: int = int(os.getenv("RAG_MAX_QUERY_LENGTH", "300"))

    # --- Rate Limiting (per IP) ---
    RATE_LIMIT_FAQ: str = os.getenv("RATE_LIMIT_FAQ", "10/minute")
    RATE_LIMIT_TIMELINE: str = os.getenv("RATE_LIMIT_TIMELINE", "30/minute")
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")

    # --- Firestore Collections ---
    COLLECTION_TIMELINES: str = "timelines"
    COLLECTION_USER_SESSIONS: str = "user_sessions"
    COLLECTION_ECI_VECTOR_DOCS: str = "eci_vector_docs"

    # --- Supported Locales ---
    SUPPORTED_LOCALES: List[str] = [
        "en-IN",  # English (India)
        "hi-IN",  # Hindi
        "mr-IN",  # Marathi
        "bn-IN",  # Bengali
        "ta-IN",  # Tamil
        "te-IN",  # Telugu
    ]
    DEFAULT_LOCALE: str = "en-IN"


settings = Settings()
