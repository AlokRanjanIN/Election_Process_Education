"""
Eligibility evaluation API endpoint.

plan.md API Design Section 1:
  POST /api/v1/eligibility/evaluate
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from core.middleware import limiter
from models.eligibility import EligibilityRequest, EligibilityResponse
from models.common import ErrorResponse
from services.eligibility_service import evaluate_eligibility

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/eligibility", tags=["Eligibility"])


@router.post(
    "/evaluate",
    response_model=EligibilityResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        429: {"description": "Rate limit exceeded"},
    },
    summary="Evaluate voter eligibility",
    description="Deterministically evaluates voter eligibility based on ECI rules. "
    "No AI is used — this is a pure rule engine.",
)
async def evaluate(request: EligibilityRequest) -> EligibilityResponse:
    """
    Evaluate voter eligibility.

    Accepts demographic information and returns eligibility status
    with the required ECI form and reasoning.
    """
    logger.info(
        "Eligibility evaluation request: state=%s, is_nri=%s",
        request.state_of_residence,
        request.is_nri,
    )

    try:
        result = evaluate_eligibility(request)
        return result
    except Exception as e:
        logger.exception("Eligibility evaluation error: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while evaluating eligibility.",
        )
