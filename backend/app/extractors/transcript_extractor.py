def extract_text_script(provided_transcript: str | None, fallback_text: str = "") -> str:
    if provided_transcript and provided_transcript.strip():
        return provided_transcript.strip()

    if fallback_text and fallback_text.strip():
        return fallback_text.strip()

    return "Transcript was not provided."

# TODO SALEKIN: Later Replace this with Whisper
