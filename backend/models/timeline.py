"""
Pydantic models for the Election Timeline API.

Matches plan.md API Design Section 3:
  GET /api/v1/timeline?state_code={code}&constituency_id={id}
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class TimelineEvent(BaseModel):
    """A single event in an election timeline."""
    phase: str = Field(
        ...,
        description="Name of the electoral phase (e.g., Nomination Deadline, Polling Day)",
        examples=["Polling Day"],
    )
    date: datetime = Field(
        ...,
        description="ISO8601 datetime of the event",
        examples=["2024-04-20T08:00:00Z"],
    )


class TimelineResponse(BaseModel):
    """
    Output payload for election timeline queries.

    Example:
        {"constituency_id": "MH-23", "events": [...]}
    """
    constituency_id: str = Field(
        ...,
        description="Constituency identifier",
        examples=["MH-23"],
    )
    events: List[TimelineEvent] = Field(
        default_factory=list,
        description="Ordered list of electoral events",
    )
