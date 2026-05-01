import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_security_headers():
    """Verify that all mandatory security headers are present in responses."""
    response = client.get("/health")
    assert response.status_code == 200
    
    # Custom security headers from middleware
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert response.headers["Cache-Control"] == "no-store, max-age=0"
    assert response.headers["Pragma"] == "no-cache"
    
    # Standard security headers
    assert "Content-Type" in response.headers

def test_cors_restrictions():
    """Verify that CORS only allows specific headers and origins (if configured)."""
    # Preflight request
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization",
    }
    response = client.options("/api/v1/faq/ask", headers=headers)
    assert response.status_code == 200
    
    # Check that only allowed headers are permitted
    allowed_headers = response.headers.get("Access-Control-Allow-Headers", "").split(", ")
    assert "Content-Type" in allowed_headers
    assert "Authorization" in allowed_headers
    # Wildcard should NOT be present if we hardened it correctly
    assert "*" not in allowed_headers

def test_invalid_dob_boundary():
    """Test boundary condition for future date of birth."""
    from datetime import date, timedelta
    future_date = (date.today() + timedelta(days=1)).isoformat()
    
    payload = {
        "dob": future_date,
        "is_citizen": True,
        "state_of_residence": "MH",
        "is_nri": False
    }
    response = client.post("/api/v1/eligibility/evaluate", json=payload)
    # Should be a validation error (400 or 422)
    assert response.status_code == 400
    assert "validation_error" in response.json()["error"]

def test_exactly_18_today():
    """Test boundary condition for someone turning 18 today."""
    from datetime import date
    today = date.today()
    dob_18 = date(today.year - 18, today.month, today.day).isoformat()
    
    payload = {
        "dob": dob_18,
        "is_citizen": True,
        "state_of_residence": "DL",
        "is_nri": False
    }
    response = client.post("/api/v1/eligibility/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["eligible"] is True
