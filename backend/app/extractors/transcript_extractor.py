import asyncio
import os
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI


for parent in Path(__file__).resolve().parents:
    env_path = parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        break


class TranscriptExtractionError(RuntimeError):
    pass


def _extract_audio_to_wav(video_path: str) -> str:
    if not shutil.which("ffmpeg"):
        raise TranscriptExtractionError("ffmpeg is required for Whisper transcription.")

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    output_path = output.name
    output.close()

    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        video_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-f",
        "wav",
        output_path,
    ]

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise TranscriptExtractionError(result.stderr.strip() or "Could not extract audio from video.")

    if os.path.getsize(output_path) == 0:
        os.unlink(output_path)
        raise TranscriptExtractionError("Extracted audio was empty.")

    return output_path


async def _transcribe_with_openai_whisper(audio_path: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise TranscriptExtractionError("OPENAI_API_KEY is not configured for OpenAI Whisper.")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )

    model = os.getenv("WHISPER_MODEL", "whisper-1")
    language = os.getenv("WHISPER_LANGUAGE")

    with open(audio_path, "rb") as audio_file:
        kwargs = {
            "file": audio_file,
            "model": model,
            "response_format": "text",
        }
        if language:
            kwargs["language"] = language

        response = await client.audio.transcriptions.create(**kwargs)

    if isinstance(response, str):
        return response.strip()

    return getattr(response, "text", "").strip()


@lru_cache(maxsize=1)
def _get_local_whisper_model():
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise TranscriptExtractionError(
            "faster-whisper is not installed for local Whisper transcription."
        ) from exc

    return WhisperModel(
        os.getenv("LOCAL_WHISPER_MODEL", "base"),
        device=os.getenv("WHISPER_DEVICE", "cpu"),
        compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
    )


def _transcribe_with_local_whisper_sync(audio_path: str) -> str:
    model = _get_local_whisper_model()
    language = os.getenv("WHISPER_LANGUAGE") or None
    segments, _ = model.transcribe(audio_path, language=language)
    return " ".join(segment.text.strip() for segment in segments).strip()


async def _transcribe_with_local_whisper(audio_path: str) -> str:
    return await asyncio.to_thread(_transcribe_with_local_whisper_sync, audio_path)


async def transcribe_video_with_whisper(video_path: str) -> str:
    provider = os.getenv("WHISPER_PROVIDER", "auto").strip().lower()

    if provider in {"", "disabled", "none", "off"}:
        return ""

    audio_path = None
    try:
        audio_path = await asyncio.to_thread(_extract_audio_to_wav, video_path)

        if provider == "openai":
            return await _transcribe_with_openai_whisper(audio_path)

        if provider in {"local", "faster-whisper", "faster_whisper"}:
            return await _transcribe_with_local_whisper(audio_path)

        if provider == "auto":
            if os.getenv("OPENAI_API_KEY"):
                return await _transcribe_with_openai_whisper(audio_path)

            try:
                return await _transcribe_with_local_whisper(audio_path)
            except TranscriptExtractionError:
                return ""

        raise TranscriptExtractionError(f"Unsupported WHISPER_PROVIDER: {provider}")
    finally:
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)


async def extract_text_script(
    video_path: str | None = None,
    provided_transcript: str | None = None,
    fallback_text: str = "",
) -> str:
    if provided_transcript and provided_transcript.strip():
        return provided_transcript.strip()

    if video_path:
        try:
            transcript = await transcribe_video_with_whisper(video_path)
            if transcript:
                return transcript
        except TranscriptExtractionError:
            pass

    if fallback_text and fallback_text.strip():
        return fallback_text.strip()

    return "Transcript was not provided."
