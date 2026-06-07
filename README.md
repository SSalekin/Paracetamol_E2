# Paracetamol_E2
Repository for our solution of E2 - ViralScore project of AI Cross Border Hackathon

## Project Architecture
![Project Architecture](./Docs/paracetamol_e2_architecture.png)

## Setups
```bash
source .venv/bin/activate

uv sync
```

## Setting up HEVC support on os
```bash
sudo apt update && sudo apt install -y ffmpeg libx265-dev x265 libavcodec-extra
```

The backend falls back to `ffmpeg` when OpenCV cannot decode HEVC/H.265 MP4 uploads.

## Whisper transcription
The backend transcribes uploaded video audio before scoring when no transcript is provided.

OpenAI Whisper:
```bash
OPENAI_API_KEY=... WHISPER_PROVIDER=openai WHISPER_MODEL=whisper-1 uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Local Whisper is also supported if `faster-whisper` is installed:
```bash
WHISPER_PROVIDER=local LOCAL_WHISPER_MODEL=base uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

Use `WHISPER_PROVIDER=auto` to prefer OpenAI Whisper when `OPENAI_API_KEY` exists, otherwise try local `faster-whisper`.

## Agent intelligence
Specialist agents use the configured Seed model by default, then fall back to deterministic local heuristics if a model call fails.

For offline testing or faster local iteration:
```bash
AGENT_LLM_ENABLED=false uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Run backend
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Run frontend
```bash
API_URL=http://localhost:8000 uv run streamlit run frontend/app.py --server.port 8501
```
