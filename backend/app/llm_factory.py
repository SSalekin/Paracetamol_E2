import os
from dataclasses import dataclass
from typing import Any, Optional

from langchain_openai import ChatOpenAI


@dataclass(frozen=True)
class ChatLLMConfig:
    model: str
    api_key: str
    base_url: Optional[str]
    temperature: float
    json_mode: bool


def _read_bool(value: Optional[str]) -> bool:
    raw = (value or "").strip().lower()
    return raw in {"1", "true", "yes", "y", "on"}


def _read_float(value: Optional[str], default: float) -> float:
    raw = (value or "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _is_placeholder(value: str) -> bool:
    raw = (value or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    return lowered.startswith("your_") or lowered.endswith("_here") or lowered == "in zalo"


def _resolve_config(
    *,
    prefix: str,
    default_model: str,
    default_api_key: str,
    default_base_url: Optional[str],
    default_temperature: float,
) -> ChatLLMConfig:
    model = os.getenv(f"{prefix}_MODEL") or default_model
    api_key = os.getenv(f"{prefix}_API_KEY") or default_api_key
    base_url = os.getenv(f"{prefix}_BASE_URL") or default_base_url
    temperature = _read_float(os.getenv(f"{prefix}_TEMPERATURE"), default_temperature)
    json_mode = _read_bool(os.getenv(f"{prefix}_JSON_MODE") or os.getenv("LLM_JSON_MODE") or "1")
    return ChatLLMConfig(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        json_mode=json_mode,
    )


class JsonModeFallbackChat:
    def __init__(self, *, primary: Any, fallback: Any):
        self._primary = primary
        self._fallback = fallback
        self._use_fallback = False

    async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
        if self._use_fallback:
            return await self._fallback.ainvoke(*args, **kwargs)
        try:
            return await self._primary.ainvoke(*args, **kwargs)
        except Exception as exc:
            try:
                result = await self._fallback.ainvoke(*args, **kwargs)
            except Exception:
                raise exc
            self._use_fallback = True
            return result

    def __getattr__(self, item: str) -> Any:
        if self._use_fallback:
            return getattr(self._fallback, item)
        return getattr(self._primary, item)


class MissingCredentialsChat:
    def __init__(self, *, prefix: str):
        self._prefix = prefix

    async def ainvoke(self, *args: Any, **kwargs: Any) -> Any:
        raise RuntimeError(
            "LLM credentials are missing. Configure one of these in .env: "
            f"{self._prefix}_API_KEY (preferred), or LLM_API_KEY, or DOLA_API_KEY."
        )


def ensure_llm_configured(*, api_key: str, env_name: str) -> None:
    value = (api_key or "").strip()
    if _is_placeholder(value):
        raise RuntimeError(f"{env_name} is not configured. Set it in .env (see env.example).")


def build_chat_llm(
    *,
    prefix: str,
    default_model: str,
    default_api_key: str,
    default_base_url: Optional[str],
    default_temperature: float = 0.0,
) -> Any:
    cfg = _resolve_config(
        prefix=prefix,
        default_model=default_model,
        default_api_key=default_api_key,
        default_base_url=default_base_url,
        default_temperature=default_temperature,
    )

    if _is_placeholder(cfg.api_key):
        return MissingCredentialsChat(prefix=prefix)

    model_kwargs = {"response_format": {"type": "json_object"}} if cfg.json_mode else {}
    primary = ChatOpenAI(
        model=cfg.model,
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        temperature=cfg.temperature,
        model_kwargs=model_kwargs,
    )

    if not cfg.json_mode:
        return primary

    fallback = ChatOpenAI(
        model=cfg.model,
        api_key=cfg.api_key,
        base_url=cfg.base_url,
        temperature=cfg.temperature,
    )
    return JsonModeFallbackChat(primary=primary, fallback=fallback)
