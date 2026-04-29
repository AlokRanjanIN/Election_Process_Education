"""
Deterministic voter eligibility evaluation service.

Implements ECI rules without AI — pure stateless rule engine.
No hallucination risk as specified in plan.md.

Rules applied:
  1. Must be an Indian citizen.
  2. Must be 18 years or older as of January 1 of the qualifying year.
  3. NRI voters use Form 6A; domestic voters use Form 6.
  4. Non-citizens and underage users are rejected with actionable reasoning.
"""

import logging
from datetime import date
from typing import Optional

from models.eligibility import EligibilityRequest, EligibilityResponse

logger = logging.getLogger(__name__)

# ECI rule: age is calculated as of January 1 of the qualifying year
MINIMUM_VOTING_AGE: int = 18


def calculate_age_as_of_jan1(dob: date, reference_year: Optional[int] = None) -> int:
    """
    Calculate age as of January 1 of the given year (ECI standard).

    The Election Commission uses January 1 of the current year as the
    qualifying date for voter registration.
    """
    if reference_year is None:
        reference_year = date.today().year
    qualifying_date = date(reference_year, 1, 1)
    age = qualifying_date.year - dob.year
    # Adjust if birthday hasn't occurred by Jan 1
    if (dob.month, dob.day) > (qualifying_date.month, qualifying_date.day):
        age -= 1
    return age


def compute_eligible_year(dob: date) -> int:
    """
    Compute the first year in which a person becomes eligible to vote.
    Eligible when they turn 18 on or before January 1 of that year.
    """
    # The person turns 18 in dob.year + 18
    turning_18_year = dob.year + MINIMUM_VOTING_AGE
    # If their birthday is after Jan 1, they won't be 18 by Jan 1 of that year
    if dob.month > 1 or (dob.month == 1 and dob.day > 1):
        return turning_18_year + 1
    return turning_18_year


def determine_required_form(is_nri: bool) -> str:
    """Determine the correct ECI registration form."""
    if is_nri:
        return "Form 6A"
    return "Form 6"


def evaluate_eligibility(request: EligibilityRequest) -> EligibilityResponse:
    """
    Evaluate voter eligibility using deterministic ECI rules.

    This is a pure function with no database or AI dependencies.
    """
    logger.info(
        "Evaluating eligibility: state=%s, is_nri=%s",
        request.state_of_residence,
        request.is_nri,
    )

    # Rule 1: Must be an Indian citizen
    if not request.is_citizen:
        return EligibilityResponse(
            eligible=False,
            required_form=None,
            reasoning="Only Indian citizens are eligible to vote in Indian elections. "
            "Please verify your citizenship status.",
        )

    # Rule 2: Must be 18+ as of January 1 of current year
    current_age = calculate_age_as_of_jan1(request.dob)

    if current_age < MINIMUM_VOTING_AGE:
        eligible_year = compute_eligible_year(request.dob)
        return EligibilityResponse(
            eligible=False,
            required_form=None,
            reasoning=(
                f"You are currently {current_age} years old (as of January 1, {date.today().year}). "
                f"The minimum voting age is {MINIMUM_VOTING_AGE}. "
                f"You will be eligible to register in {eligible_year}."
            ),
            eligible_from_year=eligible_year,
        )

    # Rule 3: Determine the correct form
    required_form = determine_required_form(request.is_nri)

    # Build reasoning based on voter type
    if request.is_nri:
        reasoning = (
            f"You are {current_age} years old, an Indian citizen, and an NRI. "
            f"You are eligible to vote. Please register using {required_form} "
            f"(for overseas electors) in the state of {request.state_of_residence}."
        )
    else:
        reasoning = (
            f"You are {current_age} years old and an Indian citizen. "
            f"You are eligible to vote. Please register using {required_form} "
            f"in the state of {request.state_of_residence}."
        )

    return EligibilityResponse(
        eligible=True,
        required_form=required_form,
        reasoning=reasoning,
    )
