"""
Unit tests for the eligibility evaluation service and API endpoint.

Tests cover:
  - Eligible adult citizen (Form 6)
  - NRI voter (Form 6A)
  - Underage voter with future eligibility year
  - Non-citizen rejection
  - Invalid state codes (400)
  - Future DOB rejection (400)
  - Missing fields rejection (400)
  - Age calculation edge cases (Jan 1 qualifying date)
"""

import pytest
from datetime import date
from unittest.mock import patch

from services.eligibility_service import (
    evaluate_eligibility,
    calculate_age_as_of_jan1,
    compute_eligible_year,
    determine_required_form,
)
from models.eligibility import EligibilityRequest


# ============================================================
# Unit Tests — Business Logic (No HTTP, No Mocking)
# ============================================================


class TestCalculateAge:
    """Test age calculation using ECI Jan 1 qualifying date."""

    def test_age_born_before_jan1(self):
        """Person born Dec 31, 2005 is older by Jan 1."""
        age = calculate_age_as_of_jan1(date(2005, 12, 31), reference_year=2024)
        assert age == 18

    def test_age_born_on_jan1(self):
        """Person born Jan 1, 2006 — exactly 18 on Jan 1, 2024."""
        age = calculate_age_as_of_jan1(date(2006, 1, 1), reference_year=2024)
        assert age == 18

    def test_age_born_after_jan1(self):
        """Person born Jan 2, 2006 — still 17 on Jan 1, 2024."""
        age = calculate_age_as_of_jan1(date(2006, 1, 2), reference_year=2024)
        assert age == 17

    def test_age_adult(self):
        """Standard adult calculation."""
        age = calculate_age_as_of_jan1(date(1990, 6, 15), reference_year=2024)
        assert age == 33

    def test_age_very_old(self):
        """Senior citizen."""
        age = calculate_age_as_of_jan1(date(1940, 3, 10), reference_year=2024)
        assert age == 83


class TestComputeEligibleYear:
    """Test future eligibility year computation."""

    def test_born_jan1(self):
        """Person born Jan 1 is eligible in the year they turn 18."""
        year = compute_eligible_year(date(2010, 1, 1))
        assert year == 2028

    def test_born_after_jan1(self):
        """Person born after Jan 1 must wait an extra year."""
        year = compute_eligible_year(date(2010, 6, 15))
        assert year == 2029

    def test_born_dec31(self):
        """Person born Dec 31 needs to wait until next year."""
        year = compute_eligible_year(date(2010, 12, 31))
        assert year == 2029


class TestDetermineForm:
    """Test form selection logic."""

    def test_domestic_voter(self):
        assert determine_required_form(is_nri=False) == "Form 6"

    def test_nri_voter(self):
        assert determine_required_form(is_nri=True) == "Form 6A"


class TestEvaluateEligibility:
    """Test the full eligibility evaluation function."""

    def test_eligible_adult_citizen(self):
        """Adult Indian citizen should be eligible with Form 6."""
        request = EligibilityRequest(
            dob=date(2000, 1, 15),
            is_citizen=True,
            state_of_residence="MH",
            is_nri=False,
        )
        result = evaluate_eligibility(request)
        assert result.eligible is True
        assert result.required_form == "Form 6"
        assert "eligible" in result.reasoning.lower()

    def test_eligible_nri(self):
        """NRI citizen should get Form 6A."""
        request = EligibilityRequest(
            dob=date(1990, 3, 20),
            is_citizen=True,
            state_of_residence="KA",
            is_nri=True,
        )
        result = evaluate_eligibility(request)
        assert result.eligible is True
        assert result.required_form == "Form 6A"
        assert "NRI" in result.reasoning

    def test_non_citizen_rejected(self):
        """Non-citizen should be ineligible."""
        request = EligibilityRequest(
            dob=date(1990, 1, 1),
            is_citizen=False,
            state_of_residence="MH",
            is_nri=False,
        )
        result = evaluate_eligibility(request)
        assert result.eligible is False
        assert result.required_form is None
        assert "citizen" in result.reasoning.lower()

    def test_underage_rejected(self):
        """Underage person should be ineligible with future year."""
        current_year = date.today().year
        request = EligibilityRequest(
            dob=date(current_year - 10, 6, 15),
            is_citizen=True,
            state_of_residence="DL",
            is_nri=False,
        )
        result = evaluate_eligibility(request)
        assert result.eligible is False
        assert result.eligible_from_year is not None
        assert result.eligible_from_year > current_year


# ============================================================
# API Tests — HTTP Endpoints
# ============================================================


class TestEligibilityAPI:
    """Test POST /api/v1/eligibility/evaluate endpoint."""

    def test_valid_eligible_request(self, client, sample_eligibility_request):
        """Valid request returns 200 with eligible=True."""
        response = client.post(
            "/api/v1/eligibility/evaluate",
            json=sample_eligibility_request,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is True
        assert data["required_form"] == "Form 6"
        assert "reasoning" in data

    def test_nri_request(self, client, sample_nri_request):
        """NRI request returns Form 6A."""
        response = client.post(
            "/api/v1/eligibility/evaluate",
            json=sample_nri_request,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is True
        assert data["required_form"] == "Form 6A"

    def test_underage_request(self, client, sample_underage_request):
        """Underage request returns eligible=False with future year."""
        response = client.post(
            "/api/v1/eligibility/evaluate",
            json=sample_underage_request,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is False
        assert data["eligible_from_year"] is not None

    def test_future_dob_rejected(self, client):
        """Future DOB returns 400."""
        response = client.post(
            "/api/v1/eligibility/evaluate",
            json={
                "dob": "2099-01-01",
                "is_citizen": True,
                "state_of_residence": "MH",
                "is_nri": False,
            },
        )
        assert response.status_code in (400, 422)

    def test_invalid_state_code(self, client):
        """Invalid state code returns 400."""
        response = client.post(
            "/api/v1/eligibility/evaluate",
            json={
                "dob": "2000-01-15",
                "is_citizen": True,
                "state_of_residence": "XX",
                "is_nri": False,
            },
        )
        assert response.status_code in (400, 422)

    def test_missing_required_fields(self, client):
        """Missing required fields returns 400/422."""
        response = client.post(
            "/api/v1/eligibility/evaluate",
            json={"dob": "2000-01-15"},
        )
        assert response.status_code in (400, 422)

    def test_invalid_date_format(self, client):
        """Invalid date format returns 400/422."""
        response = client.post(
            "/api/v1/eligibility/evaluate",
            json={
                "dob": "not-a-date",
                "is_citizen": True,
                "state_of_residence": "MH",
                "is_nri": False,
            },
        )
        assert response.status_code in (400, 422)

    def test_non_citizen_response(self, client):
        """Non-citizen returns eligible=False."""
        response = client.post(
            "/api/v1/eligibility/evaluate",
            json={
                "dob": "1990-01-01",
                "is_citizen": False,
                "state_of_residence": "MH",
                "is_nri": False,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["eligible"] is False
