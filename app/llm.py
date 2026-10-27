import json
import re
from typing import Any, Optional

import httpx

from app import config
from app.logging_config import get_logger

logger = get_logger("llm")

AUTO_ORDER = ("anthropic", "gemini", "groq", "ollama")


def has_claude() -> bool:
    return bool(config.ANTHROPIC_API_KEY)


def has_llm() -> bool:
    return active_provider() != "heuristic"


def active_provider() -> str:
    pref = (config.LLM_PROVIDER or "auto").lower()
    if pref == "heuristic":
        logger.debug("LLM provider explicitly set to heuristic")
        return "heuristic"
    if pref == "auto":
        for name in AUTO_ORDER:
            if provider_ready(name):
                logger.info(f"LLM auto-selected provider '{name}'")
                return name
        logger.info("No configured external LLM found; falling back to heuristic engine")
        return "heuristic"
    if pref in AUTO_ORDER and provider_ready(pref):
        logger.info(f"LLM provider active: '{pref}'")
        return pref
    logger.warning(f"Preferred provider '{pref}' not ready; falling back to heuristic")
    return "heuristic"


def provider_ready(name: str) -> bool:
    if name == "anthropic":
        return bool(config.ANTHROPIC_API_KEY)
    if name == "gemini":
        return bool(config.GEMINI_API_KEY)
    if name == "groq":
        return bool(config.GROQ_API_KEY)
    if name == "ollama":
        return _ollama_up()
    if name == "heuristic":
        return True
    return False


def status() -> dict[str, Any]:
    provider = active_provider()
    return {
        "provider": provider,
        "llm": provider != "heuristic",
        "claude": provider == "anthropic",
        "available": {
            "anthropic": provider_ready("anthropic"),
            "gemini": provider_ready("gemini"),
            "groq": provider_ready("groq"),
            "ollama": provider_ready("ollama"),
            "heuristic": True,
        },
    }


def complete_json(system: str, user: str, max_tokens: int = 2000) -> tuple[dict[str, Any], str]:
    """Call the active LLM and parse JSON. Raises if provider is heuristic or the call fails."""
    provider = active_provider()
    if provider == "heuristic":
        logger.warning("complete_json called but active provider is heuristic")
        raise RuntimeError("No LLM provider configured")
    logger.debug(f"Calling LLM provider '{provider}' for JSON completion (max_tokens={max_tokens})")
    try:
        text = complete_text(system, user, max_tokens=max_tokens, provider=provider)
        res = _extract_json(text)
        logger.debug(f"Successfully received and parsed JSON from provider '{provider}'")
        return res, provider
    except Exception as exc:
        logger.error(f"LLM call to '{provider}' failed: {exc}; fallback will trigger if available")
        raise


def claude_json(system: str, user: str, max_tokens: int = 2000) -> tuple[dict[str, Any], str]:
    """Back-compat alias. Second value is now the provider name, not raw text."""
    return complete_json(system, user, max_tokens=max_tokens)


def complete_text(system: str, user: str, max_tokens: int = 2000, provider: Optional[str] = None) -> str:
    name = provider or active_provider()
    if name == "anthropic":
        return _anthropic_text(system, user, max_tokens)
    if name == "gemini":
        return _gemini_text(system, user, max_tokens)
    if name == "groq":
        return _groq_text(system, user, max_tokens)
    if name == "ollama":
        return _ollama_text(system, user, max_tokens)
    raise RuntimeError(f"Unsupported LLM provider: {name}")


def _anthropic_text(system: str, user: str, max_tokens: int) -> str:
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in msg.content if getattr(block, "type", None) == "text")


def _gemini_text(system: str, user: str, max_tokens: int) -> str:
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")
    model = config.GEMINI_MODEL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.2},
    }
    data = _http_json(
        "POST",
        url,
        params={"key": config.GEMINI_API_KEY},
        json=payload,
        timeout=45.0,
    )
    parts = (((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or [])
    text = "".join(p.get("text") or "" for p in parts)
    if not text.strip():
        raise ValueError(f"Gemini returned empty text: {str(data)[:400]}")
    return text


def _groq_text(system: str, user: str, max_tokens: int) -> str:
    if not config.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not set")
    data = _http_json(
        "POST",
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {config.GROQ_API_KEY}"},
        json={
            "model": config.GROQ_MODEL,
            "temperature": 0.2,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=45.0,
    )
    text = (((data.get("choices") or [{}])[0].get("message") or {}).get("content")) or ""
    if not str(text).strip():
        raise ValueError(f"Groq returned empty text: {str(data)[:400]}")
    return str(text)


def _ollama_text(system: str, user: str, max_tokens: int) -> str:
    data = _http_json(
        "POST",
        f"{config.OLLAMA_BASE_URL}/api/chat",
        json={
            "model": config.OLLAMA_MODEL,
            "stream": False,
            "options": {"num_predict": max_tokens},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=120.0,
    )
    text = (data.get("message") or {}).get("content") or data.get("response") or ""
    if not str(text).strip():
        raise ValueError(f"Ollama returned empty text: {str(data)[:400]}")
    return str(text)


def _ollama_up() -> bool:
    try:
        _http_json("GET", f"{config.OLLAMA_BASE_URL}/api/tags", timeout=0.4)
        return True
    except Exception:
        return False


def _http_json(
    method: str,
    url: str,
    *,
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
    json: Optional[dict] = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    with httpx.Client(timeout=timeout) as client:
        res = client.request(method, url, params=params, headers=headers, json=json)
        res.raise_for_status()
        return res.json()


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        data = json.loads(text[start : end + 1])
        if isinstance(data, dict):
            return data
    raise ValueError(f"LLM did not return JSON: {text[:400]}")


def optional_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    return s or None
