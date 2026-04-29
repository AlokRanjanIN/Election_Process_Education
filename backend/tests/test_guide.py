"""
Unit tests for the guide service and API endpoint.

Tests cover:
  - All valid state transitions (INIT through COMPLETE)
  - Invalid state handling
  - Response structure (instructions, links, step numbers)
  - Default state (INIT when no param)
  - State machine completeness
"""

import pytest
from services.guide_service import (
    get_next_step,
    get_valid_states,
    STATE_MACHINE,
    TOTAL_STEPS,
)


# ============================================================
# Unit Tests — State Machine Logic
# ============================================================


class TestGuideStateMachine:
    """Test the registration state machine."""

    def test_all_states_defined(self):
        """Every state should be in the state machine."""
        expected = [
            "INIT", "DOCUMENTS_CHECKLIST", "FORM_SELECTION",
            "FORM_DOWNLOADED", "FORM_FILLING", "FORM_SUBMITTED",
            "VERIFICATION", "COMPLETE",
        ]
        for state in expected:
            assert state in STATE_MACHINE, f"Missing state: {state}"

    def test_init_state(self):
        """INIT should guide to DOCUMENTS_CHECKLIST."""
        result = get_next_step("INIT")
        assert result is not None
        assert result.current_state == "INIT"
        assert result.next_state == "DOCUMENTS_CHECKLIST"
        assert result.step_number == 1
        assert result.total_steps == TOTAL_STEPS

    def test_full_workflow_traversal(self):
        """Traverse the entire workflow from INIT to COMPLETE."""
        state = "INIT"
        visited = []
        max_iterations = 20  # Safety limit

        while state != "COMPLETE" and max_iterations > 0:
            result = get_next_step(state)
            assert result is not None, f"State '{state}' returned None"
            visited.append(state)
            state = result.next_state
            max_iterations -= 1

        assert "INIT" in visited
        assert state == "COMPLETE"
        assert max_iterations > 0, "State machine has a cycle!"

    def test_complete_state_stays(self):
        """COMPLETE state should loop back to COMPLETE."""
        result = get_next_step("COMPLETE")
        assert result is not None
        assert result.next_state == "COMPLETE"

    def test_each_step_has_instructions(self):
        """Every state should have non-empty instructions."""
        for state_name in STATE_MACHINE:
            result = get_next_step(state_name)
            assert result is not None
            assert len(result.instructions) > 10, f"State '{state_name}' has empty instructions"

    def test_each_step_has_links(self):
        """Every state should have at least one link."""
        for state_name in STATE_MACHINE:
            result = get_next_step(state_name)
            assert result is not None
            assert len(result.links) > 0, f"State '{state_name}' has no links"

    def test_invalid_state_returns_none(self):
        """Invalid state should return None."""
        result = get_next_step("NONEXISTENT")
        assert result is None

    def test_case_insensitive_state(self):
        """States should work case-insensitively."""
        result = get_next_step("init")
        assert result is not None
        assert result.current_state == "INIT"

    def test_get_valid_states(self):
        """get_valid_states should return all defined states."""
        states = get_valid_states()
        assert len(states) == len(STATE_MACHINE)
        assert "INIT" in states

    def test_step_numbers_sequential(self):
        """Step numbers should progress sequentially."""
        state = "INIT"
        prev_step = 0
        visited = set()

        while state not in visited:
            visited.add(state)
            result = get_next_step(state)
            if result is None:
                break
            assert result.step_number >= prev_step, (
                f"Step number decreased: {prev_step} -> {result.step_number}"
            )
            prev_step = result.step_number
            state = result.next_state


# ============================================================
# API Tests — HTTP Endpoint
# ============================================================


class TestGuideAPI:
    """Test GET /api/v1/guide/next-step endpoint."""

    def test_default_state(self, client):
        """No state param defaults to INIT."""
        response = client.get("/api/v1/guide/next-step")
        assert response.status_code == 200
        data = response.json()
        assert data["current_state"] == "INIT"
        assert data["next_state"] == "DOCUMENTS_CHECKLIST"

    def test_explicit_init_state(self, client):
        """Explicit INIT state works."""
        response = client.get("/api/v1/guide/next-step?current_state=INIT")
        assert response.status_code == 200
        data = response.json()
        assert data["current_state"] == "INIT"

    def test_form_downloaded_state(self, client):
        """FORM_DOWNLOADED state returns correct next step."""
        response = client.get(
            "/api/v1/guide/next-step?current_state=FORM_DOWNLOADED"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["current_state"] == "FORM_DOWNLOADED"
        assert data["next_state"] == "FORM_FILLING"

    def test_invalid_state_returns_400(self, client):
        """Invalid state returns 400 with valid states list."""
        response = client.get(
            "/api/v1/guide/next-step?current_state=INVALID_STATE"
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_response_has_links(self, client):
        """Response should include links array."""
        response = client.get("/api/v1/guide/next-step?current_state=INIT")
        assert response.status_code == 200
        data = response.json()
        assert "links" in data
        assert isinstance(data["links"], list)
        assert len(data["links"]) > 0

    def test_response_has_step_numbers(self, client):
        """Response should include step_number and total_steps."""
        response = client.get("/api/v1/guide/next-step?current_state=INIT")
        assert response.status_code == 200
        data = response.json()
        assert "step_number" in data
        assert "total_steps" in data
        assert data["step_number"] >= 1
        assert data["total_steps"] == TOTAL_STEPS
