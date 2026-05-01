"""
FAQ / RAG Assistant API endpoint.

plan.md API Design Section 4:
  POST /api/v1/faq/ask

Implements full security pipeline:
  1. Input sanitization
  2. Query length validation (max 300 chars)
  3. Prompt injection detection
  4. PII scrubbing
  5. Translation (non-English → English → process → translate back)
  6. RAG pipeline invocation
"""

import logging

from fastapi import APIRouter, HTTPException, Request, Depends
from google.cloud.firestore_v1.client import Client as FirestoreClient
from core.deps import get_db
from core.config import settings
from core.middleware import limiter
from core.security import (
    detect_prompt_injection,
    validate_query_length,
    sanitize_input,
    detect_pii,
    scrub_pii,
)
from models.faq import FAQRequest, FAQResponse, Citation
from models.common import ErrorResponse
from services.rag_service import ask_faq, OUT_OF_SCOPE_RESPONSE
from services.translation_service import (
    is_english_locale,
    translate_to_english,
    translate_from_english,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/faq", tags=["FAQ"])

# --- Out-of-scope / blocked response ---
BLOCKED_RESPONSE = FAQResponse(
    answer="I can only provide information related to the Indian Election System and ECI guidelines. "
    "Your query has been blocked for security reasons.",
    citations=[],
    locale="en-IN",
)


@router.post(
    "/ask",
    response_model=FAQResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or blocked query"},
        429: {"description": "Rate limit exceeded"},
    },
    summary="Ask the FAQ assistant",
    description="Queries the AI assistant for verified ECI information using the RAG pipeline. "
    "All responses are grounded in official ECI documents with mandatory citations.",
)
@limiter.limit(settings.RATE_LIMIT_FAQ)
async def ask(request: Request, body: FAQRequest, db: FirestoreClient = Depends(get_db)) -> FAQResponse:
    """
    Process a user question through the full security + RAG pipeline.

    Security chain:
      1. Sanitize input
      2. Validate query length
      3. Detect prompt injection
      4. Detect and scrub PII
      5. Translate if non-English locale
      6. Run RAG pipeline
      7. Translate response back if needed
    """
    # --- Step 1: Sanitize input ---
    clean_query = sanitize_input(body.query)

    # --- Step 2: Validate query length ---
    is_valid, error_msg = validate_query_length(
        clean_query,
        max_length=settings.RAG_MAX_QUERY_LENGTH,
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    # --- Step 3: Detect prompt injection ---
    is_injection, injection_msg = detect_prompt_injection(clean_query)
    if is_injection:
        logger.warning(
            "Prompt injection blocked: query='%s', reason='%s'",
            clean_query[:50],
            injection_msg,
        )
        return BLOCKED_RESPONSE

    # --- Step 4: Detect and scrub PII ---
    pii_types = detect_pii(clean_query)
    if pii_types:
        clean_query = scrub_pii(clean_query)
        logger.info("PII scrubbed from query: types=%s", pii_types)

    # --- Step 5: Translate to English if needed ---
    english_query = clean_query
    if not is_english_locale(body.locale):
        english_query = translate_to_english(clean_query, body.locale)

    # --- Step 6: Run RAG pipeline ---
    try:
        result = await ask_faq(db, english_query, body.locale)
    except Exception as e:
        logger.exception("RAG pipeline error: %s", e)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question. Please try again.",
        )

    # --- Step 7: Translate response back if needed ---
    if not is_english_locale(body.locale):
        result.answer = translate_from_english(result.answer, body.locale)
        result.locale = body.locale

    return result
