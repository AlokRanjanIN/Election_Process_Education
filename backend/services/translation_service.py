"""
Translation service using Google Cloud Translation API.

Implements plan.md Accessibility Design Section 1:
  - Translates non-English queries to English before RAG processing
  - Translates English RAG responses back to user's locale
  - Supports: en-IN, hi-IN, mr-IN, bn-IN, ta-IN, te-IN
"""

import logging
from typing import Optional

from core.config import settings

logger = logging.getLogger(__name__)

# Map locale codes to BCP-47 language codes for Cloud Translation
LOCALE_TO_LANG: dict[str, str] = {
    "en-IN": "en",
    "hi-IN": "hi",
    "mr-IN": "mr",
    "bn-IN": "bn",
    "ta-IN": "ta",
    "te-IN": "te",
}

# Reverse mapping for display
LANG_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
    "mr": "मराठी (Marathi)",
    "bn": "বাংলা (Bengali)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
}

_translate_client = None


def _get_translate_client():
    """Lazy-initialize the Translation API client."""
    global _translate_client
    if _translate_client is None:
        from google.cloud import translate_v2 as translate
        _translate_client = translate.Client()
        logger.info("Google Cloud Translation client initialized.")
    return _translate_client


def get_language_code(locale: str) -> str:
    """Extract the language code from a locale string."""
    return LOCALE_TO_LANG.get(locale, "en")


def is_english_locale(locale: str) -> bool:
    """Check if the locale is English."""
    return get_language_code(locale) == "en"


def translate_to_english(text: str, source_locale: str) -> str:
    """
    Translate text from source locale to English for RAG processing.

    Args:
        text: Input text in source language.
        source_locale: Source locale (e.g., "hi-IN").

    Returns:
        Translated English text. Returns original if already English
        or if translation fails.
    """
    if is_english_locale(source_locale):
        return text

    source_lang = get_language_code(source_locale)

    try:
        client = _get_translate_client()
        result = client.translate(
            text,
            target_language="en",
            source_language=source_lang,
        )
        translated = result.get("translatedText", text)
        logger.info(
            "Translated to English: lang=%s, original='%s', translated='%s'",
            source_lang,
            text[:50],
            translated[:50],
        )
        return translated
    except Exception as e:
        logger.warning("Translation to English failed: %s", e)
        return text


def translate_from_english(text: str, target_locale: str) -> str:
    """
    Translate English text to the target locale for user response.

    Args:
        text: English text to translate.
        target_locale: Target locale (e.g., "hi-IN").

    Returns:
        Translated text. Returns original if target is English
        or if translation fails.
    """
    if is_english_locale(target_locale):
        return text

    target_lang = get_language_code(target_locale)

    try:
        client = _get_translate_client()
        result = client.translate(
            text,
            target_language=target_lang,
            source_language="en",
        )
        translated = result.get("translatedText", text)
        logger.info(
            "Translated from English to %s: '%s' -> '%s'",
            target_lang,
            text[:50],
            translated[:50],
        )
        return translated
    except Exception as e:
        logger.warning("Translation from English failed: %s", e)
        return text


def detect_language(text: str) -> Optional[str]:
    """
    Detect the language of input text.

    Returns:
        BCP-47 language code (e.g., "hi"), or None if detection fails.
    """
    try:
        client = _get_translate_client()
        result = client.detect_language(text)
        lang = result.get("language", None)
        confidence = result.get("confidence", 0.0)
        logger.info(
            "Language detected: lang=%s, confidence=%.2f, text='%s'",
            lang,
            confidence,
            text[:50],
        )
        return lang
    except Exception as e:
        logger.warning("Language detection failed: %s", e)
        return None
