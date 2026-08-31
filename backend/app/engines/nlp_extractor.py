import json
import logging
import re
import uuid
from typing import Dict, Any, Optional
from app.config import settings
from app.engines.regex_fallback import parse_life_event_regex
from app.engines.openrouter_client import call_openrouter
from app.schemas.models import LifeEvent

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are the NLP Intake Engine for LifeEvent, an Indian government public service navigator.
Analyze the user's natural language description and extract the life event in strict JSON format.

SUPPORTED SCENARIOS:
1. "relocation": Moving, shifting, or transferring residential location between cities/states (extract "origin" and "destination" if mentioned).
2. "financial_fraud": Unauthorized transactions, UPI debits, phishing, financial cyber scams.
3. "marriage": Getting married, wedding, marital status changes.
4. "family_death": Demise or death of a family member (father, mother, spouse, parent).

If the input is an unsupported life event (e.g. starting a business, childbirth, college admission, retirement):
Set "is_supported": false and "message": "This prototype currently supports relocation, financial fraud, marriage, and family-death scenarios."

OUTPUT JSON FORMAT (ONLY valid JSON, no markdown code blocks, no backticks, no extra text):
{
  "event_type": "relocation" | "financial_fraud" | "marriage" | "family_death" | "unknown" | "<unsupported_name>",
  "origin": "City Name" | null,
  "destination": "City Name" | null,
  "confidence": 0.95,
  "is_supported": true | false,
  "message": "Human readable event summary"
}
"""


def _clean_json_text(text: str) -> str:
    """Strip markdown code block fences if present."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def extract_life_event(message: str) -> LifeEvent:
    """
    Life Event Analysis Service:
    1. If OPENROUTER_API_KEY is configured, attempts LLM parsing via OpenRouter.
    2. Gracefully falls back to the deterministic regex engine on any error, timeout, or missing key.
    """
    cleaned_input = (message or "").strip()
    event_id = f"evt_{uuid.uuid4().hex[:8]}"

    if not cleaned_input:
        return LifeEvent(
            id=event_id,
            raw_input="",
            event_type="unknown",
            origin=None,
            destination=None,
            confidence=0.0,
            is_supported=False,
            message="Please enter what happened (e.g., 'I moved from Mumbai to Pune.')."
        )

    # 1. Attempt LLM Parsing via OpenRouter if key exists
    if settings.OPENROUTER_API_KEY.strip():
        try:
            llm_raw = call_openrouter(
                messages=[{"role": "user", "content": cleaned_input}],
                system_prompt=EXTRACTION_SYSTEM_PROMPT,
                temperature=0.1,
                max_tokens=300,
                timeout_seconds=25.0
            )

            if llm_raw:
                cleaned_json = _clean_json_text(llm_raw)
                data = json.loads(cleaned_json)

                event_type = data.get("event_type", "unknown")
                is_supported = data.get("is_supported", False)
                origin = data.get("origin")
                destination = data.get("destination")
                confidence = float(data.get("confidence", 0.90))
                msg = data.get("message", "Event identified")

                if event_type == "relocation":
                    msg = f"Relocation detected: {origin or 'Mumbai'} → {destination or 'Pune'}"
                elif event_type == "financial_fraud":
                    msg = "Financial Cyber Fraud / Unauthorized Transaction detected"
                elif event_type == "marriage":
                    msg = "Marriage / Civil Status Change detected"
                elif event_type == "family_death":
                    msg = "Family Demise & Vital Records detected"

                logger.info(f"OpenRouter successfully analyzed life event: {event_type}")
                return LifeEvent(
                    id=event_id,
                    raw_input=cleaned_input,
                    event_type=event_type,
                    origin=origin,
                    destination=destination,
                    confidence=confidence,
                    is_supported=is_supported,
                    message=msg
                )
        except Exception as e:
            logger.warning(f"OpenRouter NLP extraction failed ({e}). Falling back to deterministic engine.")

    # 2. Deterministic Regex Parser Execution (Fallback / Default)
    parsed_data = parse_life_event_regex(cleaned_input)

    return LifeEvent(
        id=event_id,
        raw_input=cleaned_input,
        event_type=parsed_data.get("event_type", "unknown"),
        origin=parsed_data.get("origin"),
        destination=parsed_data.get("destination"),
        confidence=parsed_data.get("confidence", 0.0),
        is_supported=parsed_data.get("is_supported", False),
        message=parsed_data.get("message", "")
    )
