from typing import Generator
from google.cloud.firestore_v1.client import Client as FirestoreClient
from core.firebase import get_firestore_client

def get_db() -> Generator[FirestoreClient, None, None]:
    """Dependency provider for Firestore client."""
    db = get_firestore_client()
    yield db
