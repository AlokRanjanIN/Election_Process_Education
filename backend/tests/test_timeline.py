"""
Unit tests for the timeline service and API endpoint.

Tests cover:
  - Valid state code queries
  - State + constituency filtering
  - Invalid state codes (400)
  - Missing required params (422)
  - Empty results (404)
  - Response structure validation
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock


# ============================================================
# API Tests — HTTP Endpoints
# ============================================================


class TestTimelineAPI:
    """Test GET /api/v1/timeline endpoint."""

    def test_missing_state_code(self, client):
        """Missing state_code returns 422."""
        response = client.get("/api/v1/timeline")
        assert response.status_code in (400, 422)

    def test_invalid_state_code(self, client):
        """Invalid state code returns 400."""
        response = client.get("/api/v1/timeline?state_code=XX")
        assert response.status_code == 400
        data = response.json()
        assert "invalid" in data["detail"].lower() or "Invalid" in data["detail"]

    def test_valid_state_code_no_results(self, client):
        """Valid state with no data returns 404."""
        # Mock Firestore to return empty
        with patch("core.firebase.get_firestore_client") as mock_get_db:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_query = MagicMock()
            mock_query.stream.return_value = iter([])
            mock_collection.where.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/timeline?state_code=MH")
            assert response.status_code == 404

    def test_valid_request_with_results(self, client):
        """Valid state with data returns 200 and timeline events."""
        # Mock Firestore document
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            "state_code": "MH",
            "constituency_id": "MH-23",
            "events": [
                {"phase": "Polling Day", "date": datetime(2024, 4, 20, 8, 0)},
                {"phase": "Nomination Deadline", "date": datetime(2024, 4, 10, 23, 59)},
            ],
        }

        with patch("core.firebase.get_firestore_client") as mock_get_db:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_query = MagicMock()
            mock_query.where.return_value = mock_query
            mock_query.stream.return_value = iter([mock_doc])
            mock_collection.where.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/timeline?state_code=MH")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
            assert data[0]["constituency_id"] == "MH-23"
            assert len(data[0]["events"]) == 2

    def test_constituency_filter(self, client):
        """Constituency filter narrows results."""
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            "state_code": "MH",
            "constituency_id": "MH-23",
            "events": [
                {"phase": "Polling Day", "date": datetime(2024, 4, 20, 8, 0)},
            ],
        }

        with patch("core.firebase.get_firestore_client") as mock_get_db:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_query = MagicMock()
            mock_query.where.return_value = mock_query
            mock_query.stream.return_value = iter([mock_doc])
            mock_collection.where.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_get_db.return_value = mock_db

            response = client.get(
                "/api/v1/timeline?state_code=MH&constituency_id=MH-23"
            )
            assert response.status_code == 200

    def test_events_sorted_by_date(self, client):
        """Events should be sorted chronologically."""
        mock_doc = MagicMock()
        mock_doc.to_dict.return_value = {
            "state_code": "MH",
            "constituency_id": "MH-23",
            "events": [
                {"phase": "Counting Day", "date": datetime(2024, 4, 25, 8, 0)},
                {"phase": "Polling Day", "date": datetime(2024, 4, 20, 8, 0)},
                {"phase": "Nomination Deadline", "date": datetime(2024, 4, 10, 23, 59)},
            ],
        }

        with patch("core.firebase.get_firestore_client") as mock_get_db:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_query = MagicMock()
            mock_query.where.return_value = mock_query
            mock_query.stream.return_value = iter([mock_doc])
            mock_collection.where.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/timeline?state_code=MH")
            assert response.status_code == 200
            events = response.json()[0]["events"]
            dates = [e["date"] for e in events]
            assert dates == sorted(dates)

    def test_state_code_case_insensitive(self, client):
        """State code should work regardless of case."""
        with patch("core.firebase.get_firestore_client") as mock_get_db:
            mock_db = MagicMock()
            mock_collection = MagicMock()
            mock_query = MagicMock()
            mock_query.stream.return_value = iter([])
            mock_collection.where.return_value = mock_query
            mock_db.collection.return_value = mock_collection
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/timeline?state_code=mh")
            # Should not fail validation — gets 404 because no data
            assert response.status_code == 404
