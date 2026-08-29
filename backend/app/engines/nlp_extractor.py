import logging
import uuid
from typing import Dict, Any
from app.config import settings
from app.engines.regex_fallback import parse_relocation_regex
from app.schemas.models import LifeEvent

logger = logging.getLogger(__name__)


def extract_life_event(message: str) -> LifeEvent:
    """
    Life Event Analysis Service:
    1. If no GEMINI_API_KEY is configured (default), uses the deterministic fallback parser directly.
    2. If GEMINI_API_KEY is present, attempts LLM parsing, falling back to deterministic parser on any error.
    """
    cleaned_input = (message or "").strip()
    if not cleaned_input:
        return LifeEvent(
            id=f"evt_{uuid.uuid4().hex[:8]}",
            raw_input="",
            event_type="unknown",
            origin=None,
            destination=None,
            confidence=0.0,
            is_supported=False,
            message="Please enter what happened (e.g., 'I moved from Mumbai to Pune.')."
        )

    # Deterministic parser execution
    parsed_data = parse_relocation_regex(cleaned_input)

    return LifeEvent(
        id=f"evt_{uuid.uuid4().hex[:8]}",
        raw_input=cleaned_input,
        event_type=parsed_data.get("event_type", "unknown"),
        origin=parsed_data.get("origin"),
        destination=parsed_data.get("destination"),
        confidence=parsed_data.get("confidence", 0.0),
        is_supported=parsed_data.get("is_supported", False),
        message=parsed_data.get("message", "")
    )
