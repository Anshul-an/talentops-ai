import json

import pytest

from app import config, llm


@pytest.fixture(autouse=True)
def isolate_llm(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "auto")
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "")
    monkeypatch.setattr(config, "GROQ_API_KEY", "")
    monkeypatch.setattr(llm, "_ollama_up", lambda: False)
    yield


def test_auto_falls_back_to_heuristic_without_keys():
    assert llm.active_provider() == "heuristic"
    assert llm.has_llm() is False
    assert llm.has_claude() is False


def test_auto_prefers_anthropic_then_gemini_then_groq(monkeypatch):
    monkeypatch.setattr(config, "GROQ_API_KEY", "gsk-test")
    assert llm.active_provider() == "groq"
    monkeypatch.setattr(config, "GEMINI_API_KEY", "gem-test")
    assert llm.active_provider() == "gemini"
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-ant-test")
    assert llm.active_provider() == "anthropic"


def test_forced_provider_without_key_uses_heuristic(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "gemini")
    assert llm.active_provider() == "heuristic"


def test_gemini_json_via_mocked_http(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "gemini")
    monkeypatch.setattr(config, "GEMINI_API_KEY", "gem-test")

    def fake_http(method, url, **kwargs):
        assert "generativelanguage.googleapis.com" in url
        assert kwargs["params"]["key"] == "gem-test"
        return {
            "candidates": [
                {"content": {"parts": [{"text": json.dumps({"fitment_score": 81, "ok": True})}]}}
            ]
        }

    monkeypatch.setattr(llm, "_http_json", fake_http)
    data, engine = llm.complete_json("sys", "user")
    assert engine == "gemini"
    assert data["fitment_score"] == 81


def test_groq_json_via_mocked_http(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "groq")
    monkeypatch.setattr(config, "GROQ_API_KEY", "gsk-test")

    def fake_http(method, url, **kwargs):
        assert "api.groq.com" in url
        assert "Bearer gsk-test" in kwargs["headers"]["Authorization"]
        return {"choices": [{"message": {"content": '{"employment_status": "employed"}'}}]}

    monkeypatch.setattr(llm, "_http_json", fake_http)
    data, engine = llm.complete_json("sys", "user")
    assert engine == "groq"
    assert data["employment_status"] == "employed"


def test_ollama_json_via_mocked_http(monkeypatch):
    monkeypatch.setattr(config, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(llm, "_ollama_up", lambda: True)

    def fake_http(method, url, **kwargs):
        assert url.endswith("/api/chat")
        return {"message": {"content": "```json\n{\"full_name\": \"Ananya Rao\"}\n```"}}

    monkeypatch.setattr(llm, "_http_json", fake_http)
    data, engine = llm.complete_json("sys", "user")
    assert engine == "ollama"
    assert data["full_name"] == "Ananya Rao"
