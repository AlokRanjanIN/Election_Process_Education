"""
Pydantic models for the Step-by-Step Voting Guide API.

Matches plan.md API Design Section 2:
  GET /api/v1/guide/next-step?current_state={state}
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class GuideLink(BaseModel):
    """An actionable link within a guide step."""
    type: str = Field(
        ...,
        description="Link type (e.g., download, portal, info)",
        examples=["download"],
    )
    url: str = Field(
        ...,
        description="URL for the resource",
        examples=["https://voters.eci.gov.in/download/form6"],
    )
    label: Optional[str] = Field(
        default=None,
        description="Human-readable label for the link",
    )


class GuideResponse(BaseModel):
    """
    Output payload for the guide next-step endpoint.

    Example:
        {
            "current_state": "INIT",
            "next_state": "DOCUMENTS_CHECKLIST",
            "instructions": "Gather the following documents...",
            "links": [...]
        }
    """
    current_state: str = Field(
        ...,
        description="The user's current state in the workflow",
    )
    next_state: str = Field(
        ...,
        description="The next state after completing this step",
    )
    instructions: str = Field(
        ...,
        description="Clear, actionable instructions for this step",
    )
    links: List[GuideLink] = Field(
        default_factory=list,
        description="Relevant resource links for this step",
    )
    step_number: int = Field(
        ...,
        description="Current step number in the workflow (1-based)",
    )
    total_steps: int = Field(
        ...,
        description="Total number of steps in the workflow",
    )
