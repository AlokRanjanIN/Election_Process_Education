"""
Security utilities for input validation, prompt injection protection,
and PII detection.

Implements plan.md Section: Security Model.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# --- Prompt Injection Patterns ---
# Detect attempts to override system instructions or inject new prompts
INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"\[system\]", re.IGNORECASE),
    re.compile(r"\[assistant\]", re.IGNORECASE),
    re.compile(r"\[user\]", re.IGNORECASE),
    re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions|prompts|rules)", re.IGNORECASE),
    re.compile(r"(you\s+are|act\s+as|pretend\s+to\s+be|roleplay)", re.IGNORECASE),
    re.compile(r"(system\s*prompt|system\s*instruction|system\s*message)", re.IGNORECASE),
    re.compile(r"<\s*/?\s*(system|prompt|instruction)", re.IGNORECASE),
    re.compile(r"(forget|disregard|override)\s+(everything|all|your)", re.IGNORECASE),
    re.compile(r"(do\s+not\s+follow|don'?t\s+follow)\s+(your|the)\s+(rules|instructions)", re.IGNORECASE),
    re.compile(r"(jailbreak|DAN|bypass\s+filter)", re.IGNORECASE),
]

# --- PII Detection Patterns (Aadhaar, EPIC, phone numbers) ---
PII_PATTERNS: dict[str, re.Pattern] = {
    "aadhaar": re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),
    "epic_id": re.compile(r"\b[A-Z]{3}\d{7}\b"),
    "phone_india": re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b"),
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
}

# --- Allowed characters (block control characters and unusual Unicode) ---
ALLOWED_QUERY_PATTERN = re.compile(r"^[\w\s.,?!;:'\"\-()/@#&%₹\u0900-\u097F\u0980-\u09FF\u0B80-\u0BFF\u0C00-\u0C7F\u0A80-\u0AFF]+$")


def detect_prompt_injection(text: str) -> Tuple[bool, str]:
    """
    Scan text for prompt injection attempts.

    Returns:
        Tuple of (is_injection_detected, matched_pattern_description)
    """
    for pattern in INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            logger.warning(
                "Prompt injection detected: pattern='%s', match='%s'",
                pattern.pattern,
                match.group(),
            )
            return True, f"Blocked: suspicious pattern detected ({match.group()[:30]})"
    return False, ""


def validate_query_length(text: str, max_length: int = 300) -> Tuple[bool, str]:
    """
    Enforce maximum query length as specified in plan.md security model.
    Queries longer than 300 characters are rejected.
    """
    if len(text.strip()) == 0:
        return False, "Query cannot be empty."
    if len(text) > max_length:
        return False, f"Query exceeds maximum length of {max_length} characters."
    return True, ""


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by stripping dangerous characters
    and normalizing whitespace.
    """
    # Remove null bytes
    text = text.replace("\x00", "")
    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def detect_pii(text: str) -> list[str]:
    """
    Detect potential PII in user input.
    Returns list of PII types found.
    """
    found: list[str] = []
    for pii_type, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            found.append(pii_type)
    if found:
        logger.info("PII detected in query: types=%s", found)
    return found


def scrub_pii(text: str) -> str:
    """Replace detected PII with redaction markers."""
    result = text
    for pii_type, pattern in PII_PATTERNS.items():
        result = pattern.sub(f"[REDACTED_{pii_type.upper()}]", result)
    return result
