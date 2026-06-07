import os
from typing import Optional

from openai import OpenAI


def is_openai_configured() -> bool:
    value = (os.getenv("OPENAI_API_KEY") or "").strip()
    return bool(value) and not value.lower().startswith("your_")


def transcribe_video_with_whisper(video_path: str) -> Optional[str]:
    if not is_openai_configured():
        return None

    client = OpenAI()
    with open(video_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model=os.getenv("WHISPER_MODEL", "whisper-1"),
            file=f,
        )

    text = getattr(result, "text", None)
    if not text:
        return None
    return str(text).strip() or None

