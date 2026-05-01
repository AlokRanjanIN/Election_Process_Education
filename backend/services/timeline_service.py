"""
Election timeline service — fetches electoral schedules from Firestore.

Queries the `timelines` collection filtered by state_code and optionally
constituency_id, as specified in plan.md database schema.
"""

import logging
import time
from typing import List, Optional
from google.cloud.firestore_v1.client import Client as FirestoreClient
from starlette.concurrency import run_in_threadpool

from core.config import settings
from models.timeline import TimelineResponse, TimelineEvent

logger = logging.getLogger(__name__)

TIMELINE_CACHE_TTL_SECONDS = 300
_timeline_cache: dict[tuple[str, Optional[str]], tuple[float, List[TimelineResponse]]] = {}


async def get_timeline(
    db: FirestoreClient,
    state_code: str,
    constituency_id: Optional[str] = None,
) -> List[TimelineResponse]:
    """
    Retrieve election timelines from Firestore.

    Args:
        state_code: Two-letter state code (e.g., "MH").
        constituency_id: Optional constituency identifier (e.g., "MH-23").

    Returns:
        List of TimelineResponse objects matching the query.
    """
    state_upper = state_code.upper()
    constituency_upper = constituency_id.upper() if constituency_id else None
    cache_key = (state_upper, constituency_upper)

    if settings.ENVIRONMENT.lower() != "testing":
        cached = _timeline_cache.get(cache_key)
        if cached and time.monotonic() - cached[0] < TIMELINE_CACHE_TTL_SECONDS:
            logger.info(
                "Timeline cache hit: state_code=%s, constituency_id=%s",
                state_upper,
                constituency_upper,
            )
            return cached[1]

    results = await run_in_threadpool(
        _fetch_timeline_from_firestore,
        db,
        state_upper,
        constituency_upper,
    )

    if results and settings.ENVIRONMENT.lower() != "testing":
        _timeline_cache[cache_key] = (time.monotonic(), results)

    return results


def _fetch_timeline_from_firestore(
    db: FirestoreClient,
    state_code: str,
    constituency_id: Optional[str] = None,
) -> List[TimelineResponse]:
    """Fetch timelines synchronously from Firestore."""
    logger.info(
        "Fetching timeline: state_code=%s, constituency_id=%s",
        state_code,
        constituency_id,
    )

    from google.cloud.firestore_v1.base_query import FieldFilter
    collection_ref = db.collection(settings.COLLECTION_TIMELINES)

    # Build query with filters
    query = collection_ref.where(
        filter=FieldFilter("state_code", "==", state_code)
    )

    if constituency_id:
        query = query.where(
            filter=FieldFilter("constituency_id", "==", constituency_id)
        )

    # Execute query
    docs = query.stream()

    results: List[TimelineResponse] = []
    for doc in docs:
        data = doc.to_dict() or {}
        events = []
        for event_data in data.get("events", []):
            events.append(
                TimelineEvent(
                    phase=event_data.get("phase", ""),
                    date=event_data.get("date"),
                )
            )
        results.append(
            TimelineResponse(
                constituency_id=data.get("constituency_id", ""),
                events=sorted(events, key=lambda e: e.date),
            )
        )

    logger.info("Timeline query returned %d results.", len(results))
    return results
