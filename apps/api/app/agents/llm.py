"""LLM client factory — routes through LiteLLM proxy when configured."""

from __future__ import annotations

from functools import lru_cache

from langchain_mistralai import ChatMistralAI

from app.config import settings

_MODEL = "mistral-large-latest"


@lru_cache(maxsize=1)
def get_llm() -> ChatMistralAI:
    kwargs: dict = {
        "model": _MODEL,
        "temperature": 0.0,
        "max_tokens": 4096,
    }

    if settings.litellm_proxy_url and settings.litellm_proxy_url != "http://localhost:4000":
        kwargs["endpoint"] = settings.litellm_proxy_url
    if settings.mistral_api_key:
        kwargs["api_key"] = settings.mistral_api_key

    return ChatMistralAI(**kwargs)
