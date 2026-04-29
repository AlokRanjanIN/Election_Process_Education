"""
Step-by-step voting guide API endpoint.

plan.md API Design Section 2:
  GET /api/v1/guide/next-step?current_state={state}
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from models.guide import GuideResponse
from models.common import ErrorResponse
from services.guide_service import get_next_step, get_valid_states

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/guide", tags=["Guide"])


@router.get(
    "/next-step",
    response_model=GuideResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid state parameter"},
        429: {"description": "Rate limit exceeded"},
    },
    summary="Get next registration step",
    description="Returns the next actionable step in the voter registration workflow "
    "based on the user's current state.",
)
async def next_step(
    current_state: str = Query(
        default="INIT",
        description="Current state in the registration workflow",
        examples=["INIT", "DOCUMENTS_CHECKLIST", "FORM_DOWNLOADED"],
    ),
) -> GuideResponse:
    """
    Get the next step in the voter registration process.

    The state machine guides users through the full registration workflow
    from initial document gathering through EPIC card issuance.
    """
    logger.info("Guide next-step request: current_state=%s", current_state)

    result = get_next_step(current_state)

    if result is None:
        valid_states = get_valid_states()
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state '{current_state}'. "
            f"Valid states are: {', '.join(valid_states)}",
        )

    return result
