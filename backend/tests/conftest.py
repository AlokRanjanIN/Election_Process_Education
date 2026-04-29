"""
Pytest fixtures and configuration for the test suite.

Provides:
  - FastAPI TestClient
  - Mocked Firestore client
  - Mocked Vertex AI services
  - Common test data factories

Strategy: Pre-mock all Google Cloud SDK modules via sys.modules before
any application code is imported. This avoids ModuleNotFoundError in tests
when GCP SDKs are not installed.
"""

import os
import sys
from datetime import date, datetime
from typing import Generator
from unittest.mock import MagicMock

import pytest

# Ensure backend is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment before importing anything
os.environ["ENVIRONMENT"] = "testing"
os.environ["GCP_PROJECT_ID"] = "test-project"
os.environ["GCP_LOCATION"] = "us-central1"

# ============================================================
# Pre-mock all Google Cloud modules in sys.modules BEFORE app import
# ============================================================

# Firebase Admin SDK
_mock_firebase_admin = MagicMock()
_mock_firebase_admin._apps = {}

sys.modules["firebase_admin"] = _mock_firebase_admin
sys.modules["firebase_admin.credentials"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()

# Google Cloud — create a proper mock package hierarchy
_mock_google = MagicMock()
_mock_google_cloud = MagicMock()
_mock_google.cloud = _mock_google_cloud

sys.modules["google"] = _mock_google
sys.modules["google.cloud"] = _mock_google_cloud

# Firestore
_mock_firestore_v1 = MagicMock()
sys.modules["google.cloud.firestore_v1"] = _mock_firestore_v1
sys.modules["google.cloud.firestore_v1.client"] = MagicMock()
sys.modules["google.cloud.firestore_v1.base_query"] = MagicMock()
sys.modules["google.cloud.firestore_v1.vector"] = MagicMock()
sys.modules["google.cloud.firestore_v1.base_vector_query"] = MagicMock()
sys.modules["google.cloud.firestore"] = MagicMock()

# Vertex AI / AI Platform
sys.modules["google.cloud.aiplatform"] = MagicMock()
sys.modules["google.cloud.aiplatform.gapic"] = MagicMock()
sys.modules["google.cloud.aiplatform.gapic.schema"] = MagicMock()
sys.modules["google.cloud.aiplatform.gapic.schema.predict"] = MagicMock()
sys.modules["vertexai"] = MagicMock()
sys.modules["vertexai.language_models"] = MagicMock()
sys.modules["vertexai.generative_models"] = MagicMock()

# Translation
sys.modules["google.cloud.translate_v2"] = MagicMock()

# ============================================================
# Now safe to import the application
# ============================================================

from main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture
def client() -> Generator:
    """Create a FastAPI TestClient with mocked dependencies."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_eligibility_request() -> dict:
    """Sample valid eligibility request."""
    return {
        "dob": "2000-01-15",
        "is_citizen": True,
        "state_of_residence": "MH",
        "is_nri": False,
    }


@pytest.fixture
def sample_underage_request() -> dict:
    """Sample underage eligibility request."""
    current_year = date.today().year
    return {
        "dob": f"{current_year - 10}-06-15",
        "is_citizen": True,
        "state_of_residence": "DL",
        "is_nri": False,
    }


@pytest.fixture
def sample_nri_request() -> dict:
    """Sample NRI eligibility request."""
    return {
        "dob": "1990-03-20",
        "is_citizen": True,
        "state_of_residence": "KA",
        "is_nri": True,
    }


@pytest.fixture
def sample_faq_request() -> dict:
    """Sample valid FAQ request."""
    return {
        "query": "How to register as a new voter?",
        "locale": "en-IN",
    }


@pytest.fixture
def sample_faq_hindi_request() -> dict:
    """Sample FAQ request in Hindi locale."""
    return {
        "query": "मतदाता पहचान पत्र कैसे बनवाएं?",
        "locale": "hi-IN",
    }


@pytest.fixture
def mock_firestore_timeline_data() -> list[dict]:
    """Sample Firestore timeline documents."""
    return [
        {
            "state_code": "MH",
            "constituency_id": "MH-23",
            "events": [
                {"phase": "Nomination Deadline", "date": datetime(2024, 4, 10, 23, 59)},
                {"phase": "Polling Day", "date": datetime(2024, 4, 20, 8, 0)},
                {"phase": "Counting Day", "date": datetime(2024, 4, 25, 8, 0)},
            ],
        }
    ]
