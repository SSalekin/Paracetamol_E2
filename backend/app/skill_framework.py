import asyncio
import hashlib
import json
import os
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple


@dataclass(frozen=True)
class SkillSpec:
    name: str
    version: str
    timeout_s: float
    retries: int


class SkillRunner:
    def __init__(self) -> None:
        max_concurrency = int(os.getenv("SKILL_MAX_CONCURRENCY", "4"))
        self._sem = asyncio.Semaphore(max_concurrency)
        self._cache: Dict[str, Any] = {}
        self._cache_order: Dict[str, float] = {}
        self._cache_max_items = int(os.getenv("SKILL_CACHE_MAX_ITEMS", "128"))

    def _make_cache_key(self, spec: SkillSpec, signals_fingerprint: str) -> str:
        return f"{spec.name}:{spec.version}:{signals_fingerprint}"

    def _prune_cache(self) -> None:
        if len(self._cache_order) <= self._cache_max_items:
            return
        items = sorted(self._cache_order.items(), key=lambda kv: kv[1])
        while len(items) > self._cache_max_items:
            key, _ts = items.pop(0)
            self._cache.pop(key, None)
            self._cache_order.pop(key, None)

    async def run(
        self,
        spec: SkillSpec,
        *,
        signals_fingerprint: str,
        fn: Callable[[], Awaitable[Any]],
    ) -> Any:
        cache_key = self._make_cache_key(spec, signals_fingerprint)
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._cache_order[cache_key] = time.time()
            return cached

        async with self._sem:
            last_error: Optional[BaseException] = None
            attempts = max(1, int(spec.retries) + 1)
            for _ in range(attempts):
                try:
                    result = await asyncio.wait_for(fn(), timeout=float(spec.timeout_s))
                    self._cache[cache_key] = result
                    self._cache_order[cache_key] = time.time()
                    self._prune_cache()
                    return result
                except Exception as exc:
                    last_error = exc
                    await asyncio.sleep(0.15)

            raise last_error or RuntimeError("Skill failed")


def fingerprint_signals(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

