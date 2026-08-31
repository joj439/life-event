import pytest
from unittest.mock import patch, MagicMock
from app.config import settings
from app.engines.openrouter_client import call_openrouter
from app.engines.nlp_extractor import extract_life_event
from app.engines.assistant_engine import generate_assistant_response


def test_openrouter_empty_key_fallback():
    """Verify that an empty API key immediately returns None without making external network calls."""
    with patch("app.engines.openrouter_client.settings.OPENROUTER_API_KEY", ""):
        result = call_openrouter(messages=[{"role": "user", "content": "Hello"}])
        assert result is None


def test_openrouter_nlp_extraction_success():
    """Verify that successful OpenRouter JSON output is properly parsed into a LifeEvent domain model."""
    mock_llm_json = """
    {
      "event_type": "financial_fraud",
      "origin": null,
      "destination": null,
      "confidence": 0.99,
      "is_supported": true,
      "message": "Financial Cyber Fraud detected"
    }
    """
    with patch("app.engines.nlp_extractor.settings.OPENROUTER_API_KEY", "test-key"):
        with patch("app.engines.nlp_extractor.call_openrouter", return_value=mock_llm_json):
            event = extract_life_event("Someone made an unauthorized UPI payment.")
            assert event.event_type == "financial_fraud"
            assert event.is_supported is True
            assert event.confidence == 0.99


def test_openrouter_nlp_extraction_fallback_on_error():
    """Verify that if OpenRouter raises an exception, NLP extraction falls back to deterministic regex."""
    with patch("app.engines.nlp_extractor.settings.OPENROUTER_API_KEY", "test-key"):
        with patch("app.engines.nlp_extractor.call_openrouter", side_effect=Exception("API connection timeout")):
            event = extract_life_event("I moved from Mumbai to Pune.")
            assert event.event_type == "relocation"
            assert event.origin == "Mumbai"
            assert event.destination == "Pune"
            assert event.is_supported is True


def test_openrouter_assistant_success():
    """Verify that successful OpenRouter text output is returned with source='openrouter_llm'."""
    mock_answer = "For financial fraud, report immediately to cybercrime.gov.in or call 1930."
    with patch("app.engines.assistant_engine.settings.OPENROUTER_API_KEY", "test-key"):
        with patch("app.engines.assistant_engine.call_openrouter", return_value=mock_answer):
            res = generate_assistant_response("Where do I report fraud?")
            assert res["source"] == "openrouter_llm"
            assert "cybercrime.gov.in" in res["answer"]


def test_openrouter_assistant_fallback_on_error():
    """Verify that assistant falls back to deterministic response if OpenRouter fails."""
    with patch("app.engines.assistant_engine.settings.OPENROUTER_API_KEY", "test-key"):
        with patch("app.engines.assistant_engine.call_openrouter", side_effect=Exception("Network error")):
            res = generate_assistant_response("Where should I report this?", life_event_id=None)
            assert res["source"] == "deterministic_fallback"
            assert len(res["answer"]) > 0
