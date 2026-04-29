"""
Pydantic models for the Eligibility Evaluation API.

Matches plan.md API Design Section 1:
  POST /api/v1/eligibility/evaluate
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# --- Valid Indian state/UT codes ---
VALID_STATE_CODES: set[str] = {
    "AN", "AP", "AR", "AS", "BR", "CH", "CT", "DD", "DL", "GA",
    "GJ", "HP", "HR", "JH", "JK", "KA", "KL", "LA", "LD", "MH",
    "ML", "MN", "MP", "MZ", "NL", "OD", "PB", "PY", "RJ", "SK",
    "TN", "TG", "TR", "UK", "UP", "WB",
}


class EligibilityRequest(BaseModel):
    """
    Input payload for voter eligibility evaluation.

    Example:
        {"dob": "2005-08-15", "is_citizen": true, "state_of_residence": "MH", "is_nri": false}
    """
    dob: date = Field(
        ...,
        description="Date of birth in YYYY-MM-DD format",
        examples=["2005-08-15"],
    )
    is_citizen: bool = Field(
        ...,
        description="Whether the user is an Indian citizen",
    )
    state_of_residence: str = Field(
        ...,
        min_length=2,
        max_length=2,
        description="Two-letter Indian state/UT code (e.g., MH, DL, KA)",
        examples=["MH"],
    )
    is_nri: bool = Field(
        default=False,
        description="Whether the user is a Non-Resident Indian",
    )

    @field_validator("dob")
    @classmethod
    def dob_must_be_in_past(cls, v: date) -> date:
        """Reject future dates of birth."""
        if v >= date.today():
            raise ValueError("Date of birth must be a valid past date.")
        return v

    @field_validator("state_of_residence")
    @classmethod
    def state_must_be_valid(cls, v: str) -> str:
        """Validate against known Indian state/UT codes."""
        v_upper = v.upper()
        if v_upper not in VALID_STATE_CODES:
            raise ValueError(
                f"Invalid state code '{v}'. Must be a valid Indian state/UT code."
            )
        return v_upper


class EligibilityResponse(BaseModel):
    """
    Output payload for voter eligibility evaluation.

    Example:
        {"eligible": true, "required_form": "Form 6", "reasoning": "User is over 18 and an Indian citizen."}
    """
    eligible: bool = Field(
        ...,
        description="Whether the user is eligible to vote",
    )
    required_form: Optional[str] = Field(
        default=None,
        description="ECI form required for registration (e.g., Form 6, Form 6A)",
    )
    reasoning: str = Field(
        ...,
        description="Human-readable explanation of the eligibility determination",
    )
    eligible_from_year: Optional[int] = Field(
        default=None,
        description="If underage, the year they become eligible",
    )
