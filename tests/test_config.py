import pytest
from pydantic import ValidationError

from src.config import Settings


def test_default_settings():
    settings = Settings(_env_file=None)

    assert settings.app_name == "AuditAgent"
    assert settings.chunk_size == 1000
    assert settings.chunk_overlap == 200
    assert settings.top_k == 4
    assert settings.rrf_k == 60
    assert settings.max_retry_count == 2


def test_invalid_chunk_size():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, chunk_size=50)


def test_invalid_chunk_overlap():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            chunk_size=1000,
            chunk_overlap=1000,
        )


def test_invalid_top_k():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, top_k=0)


def test_retry_limit_cannot_exceed_two():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, max_retry_count=3)


def test_configuration_does_not_require_api_keys(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    settings = Settings(_env_file=None)

    assert settings.groq_api_key is None
    assert settings.tavily_api_key is None