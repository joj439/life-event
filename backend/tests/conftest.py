import pytest
from app.config import settings


@pytest.fixture(autouse=True)
def disable_external_llm_calls_for_unit_tests(monkeypatch, request):
    """
    By default in unit/regression tests, ensure tests run fast and deterministically
    without consuming rate limits or making external HTTP requests, unless
    explicitly testing the OpenRouter module in test_openrouter.py.
    """
    if "test_openrouter" not in request.node.fspath.basename:
        monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "")
