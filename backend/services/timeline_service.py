"""
Election timeline service — fetches electoral schedules from Firestore.

Queries the `timelines` collection filtered by state_code and optionally
constituency_id, as specified in plan.md database schema.
"""

import logging
from typing import List, Optional

from core.config import settings
from models.timeline import TimelineResponse, TimelineEvent

logger = logging.getLogger(__name__)


async def get_timeline(
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
    logger.info(
        "Fetching timeline: state_code=%s, constituency_id=%s",
        state_code,
        constituency_id,
    )

    from google.cloud.firestore_v1.base_query import FieldFilter
    from core.firebase import get_firestore_client

    db = get_firestore_client()
    collection_ref = db.collection(settings.COLLECTION_TIMELINES)

    # Build query with filters
    query = collection_ref.where(
        filter=FieldFilter("state_code", "==", state_code.upper())
    )

    if constituency_id:
        query = query.where(
            filter=FieldFilter("constituency_id", "==", constituency_id.upper())
        )

    # Execute query
    docs = query.stream()

    results: List[TimelineResponse] = []
    for doc in docs:
        data = doc.to_dict()
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
