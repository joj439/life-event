import logging
import httpx
from typing import List, Dict, Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_CHAT_ENDPOINT = f"{settings.OPENROUTER_BASE_URL.rstrip('/')}/chat/completions"


def call_openrouter(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: int = 800,
    timeout_seconds: float = 30.0
) -> Optional[str]:
    """
    Synchronous helper to execute an LLM call via OpenRouter.
    Returns the string completion text on success, or None on failure/missing key.
    """
    api_key = settings.OPENROUTER_API_KEY.strip()
    if not api_key:
        logger.info("OpenRouter API key not configured. Using deterministic engine.")
        return None

    formatted_messages = []
    if system_prompt:
        formatted_messages.append({"role": "system", "content": system_prompt})
    formatted_messages.extend(messages)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://life-event.navigator",
        "X-Title": "LifeEvent Navigator",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.OPENROUTER_MODEL or "openrouter/free",
        "messages": formatted_messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.post(
                OPENROUTER_CHAT_ENDPOINT,
                headers=headers,
                json=payload
            )

            if response.status_code != 200:
                logger.warning(
                    f"OpenRouter API returned error status {response.status_code}: {response.text[:200]}"
                )
                return None

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                logger.warning("OpenRouter API response contained empty choices.")
                return None

            content = choices[0].get("message", {}).get("content", "")
            return content.strip() if content else None

    except httpx.TimeoutException:
        logger.warning("OpenRouter API call timed out. Falling back to deterministic engine.")
        return None
    except Exception as e:
        logger.warning(f"OpenRouter API call encountered error: {e}. Falling back to deterministic engine.")
        return None
