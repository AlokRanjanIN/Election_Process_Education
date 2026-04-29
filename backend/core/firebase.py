"""
Firebase Admin SDK and Firestore client initialization.

On Cloud Run, authentication uses Application Default Credentials (ADC)
attached to the service's IAM role — no JSON key files needed.
Locally, set GOOGLE_APPLICATION_CREDENTIALS env var to a service account key.
"""

import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.client import Client as FirestoreClient

from core.config import settings

logger = logging.getLogger(__name__)

_firestore_client: Optional[FirestoreClient] = None


def initialize_firebase() -> None:
    """Initialize the Firebase Admin SDK (idempotent)."""
    if not firebase_admin._apps:
        try:
            # On Cloud Run: uses ADC automatically
            # Locally: uses GOOGLE_APPLICATION_CREDENTIALS
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                "projectId": settings.GCP_PROJECT_ID,
            })
            logger.info(
                "Firebase Admin SDK initialized for project: %s",
                settings.GCP_PROJECT_ID,
            )
        except Exception as e:
            logger.warning(
                "Firebase ADC init failed, attempting without credentials: %s", e
            )
            firebase_admin.initialize_app(options={
                "projectId": settings.GCP_PROJECT_ID,
            })


def get_firestore_client() -> FirestoreClient:
    """Return a singleton Firestore client instance."""
    global _firestore_client
    if _firestore_client is None:
        initialize_firebase()
        _firestore_client = firestore.client()
        logger.info("Firestore client created.")
    return _firestore_client
