"""
Pydantic models for the FAQ / RAG Assistant API.

Matches plan.md API Design Section 4:
  POST /api/v1/faq/ask
"""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from core.config import settings


class FAQRequest(BaseModel):
    """
    Input payload for the FAQ assistant.

    Example:
        {"query": "How to vote if I am blind?", "locale": "en-IN"}
    """
    query: str = Field(
        ...,
        min_length=3,
        max_length=300,
        description="Natural language question about the Indian election process",
        examples=["How to vote if I am blind?"],
    )
    locale: str = Field(
        default="en-IN",
        description="User's preferred locale for response language",
        examples=["en-IN", "hi-IN"],
    )

    @field_validator("locale")
    @classmethod
    def locale_must_be_supported(cls, v: str) -> str:
        """Fall back to default locale if unsupported."""
        if v not in settings.SUPPORTED_LOCALES:
            return settings.DEFAULT_LOCALE
        return v

    @field_validator("query")
    @classmethod
    def query_must_not_be_blank(cls, v: str) -> str:
        """Reject whitespace-only queries."""
        if not v.strip():
            raise ValueError("Query cannot be blank.")
        return v.strip()


class Citation(BaseModel):
    """A source citation for an FAQ response."""
    title: str = Field(
        ...,
        description="Title of the source document",
        examples=["ECI Guidelines for PwD"],
    )
    url: str = Field(
        ...,
        description="URL to the official source",
        examples=["https://eci.gov.in/pwd-guidelines"],
    )


class FAQResponse(BaseModel):
    """
    Output payload for the FAQ assistant.

    Example:
        {
            "answer": "Visually impaired voters are permitted...",
            "citations": [{"title": "...", "url": "..."}]
        }
    """
    answer: str = Field(
        ...,
        description="AI-generated answer grounded in ECI documents",
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="Source documents used to generate the answer",
    )
    locale: Optional[str] = Field(
        default="en-IN",
        description="Locale of the response",
    )
