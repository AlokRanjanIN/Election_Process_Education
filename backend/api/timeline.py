"""
Election timeline API endpoint.

plan.md API Design Section 3:
  GET /api/v1/timeline?state_code={code}&constituency_id={id}
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Request

from core.config import settings
from core.middleware import limiter
from models.timeline import TimelineResponse
from models.common import ErrorResponse
from models.eligibility import VALID_STATE_CODES
from services.timeline_service import get_timeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/timeline", tags=["Timeline"])


@router.get(
    "",
    response_model=List[TimelineResponse],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        404: {"model": ErrorResponse, "description": "No timelines found"},
        429: {"description": "Rate limit exceeded"},
    },
    summary="Fetch electoral timeline",
    description="Retrieves the schedule of elections for a specific state and/or constituency.",
)
@limiter.limit(settings.RATE_LIMIT_TIMELINE)
async def fetch_timeline(
    request: Request,
    state_code: str = Query(
        ...,
        min_length=2,
        max_length=2,
        description="Two-letter Indian state/UT code (e.g., MH)",
        examples=["MH"],
    ),
    constituency_id: Optional[str] = Query(
        default=None,
        description="Constituency identifier (e.g., MH-23)",
        examples=["MH-23"],
    ),
) -> List[TimelineResponse]:
    """
    Fetch electoral timeline for a state/constituency.

    Returns a list of timeline events including nomination deadlines,
    polling days, and counting dates.
    """
    # Validate state code
    state_upper = state_code.upper().strip()
    if state_upper not in VALID_STATE_CODES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid state code '{state_code}'. Must be a valid Indian state/UT code.",
        )

    logger.info(
        "Timeline request: state_code=%s, constituency_id=%s",
        state_upper,
        constituency_id,
    )

    try:
        results = await get_timeline(
            state_code=state_upper,
            constituency_id=constituency_id.upper().strip() if constituency_id else None,
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No election timeline found for state '{state_upper}'"
                + (f" and constituency '{constituency_id}'" if constituency_id else "")
                + ". Timeline data may not yet be available for this region.",
            )

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Timeline fetch error: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while fetching timeline data.",
        )
