import asyncio
import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class VideoScoreCacheKey:
    video_id: str
    params_json: str

    def to_string(self) -> str:
        return f"{self.video_id}|{self.params_json}"


def _stable_params_json(params: dict[str, Any]) -> str:
    return json.dumps(params, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


class VideoScoreCache:
    def __init__(self, max_items: int = 2) -> None:
        self._max_items = max_items
        self._lock = asyncio.Lock()
        self._items: OrderedDict[str, Any] = OrderedDict()

    def make_key(self, *, video_id: str, params: dict[str, Any]) -> VideoScoreCacheKey:
        return VideoScoreCacheKey(video_id=video_id, params_json=_stable_params_json(params))

    async def get(self, key: VideoScoreCacheKey) -> Optional[Any]:
        k = key.to_string()
        async with self._lock:
            if k not in self._items:
                return None
            self._items.move_to_end(k)
            return self._items[k]

    async def set(self, key: VideoScoreCacheKey, value: Any) -> None:
        k = key.to_string()
        async with self._lock:
            if k in self._items:
                self._items.move_to_end(k)
                self._items[k] = value
            else:
                self._items[k] = value
                self._items.move_to_end(k)
            while len(self._items) > self._max_items:
                self._items.popitem(last=False)
