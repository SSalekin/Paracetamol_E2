# Paracetamol_E2
Repository for our solution of E2 - ViralScore project of AI Cross Border Hackathon


## Setup
```bash
source .venv/bin/activate

uv sync
```

## Setting up HEVC support on os
```bash
sudo apt update && sudo apt install -y ffmpeg libx265-dev x265 libavcodec-extra
```

The backend falls back to `ffmpeg` when OpenCV cannot decode HEVC/H.265 MP4 uploads.

## Run backend
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

## Run frontend
```bash
API_URL=http://localhost:8000 uv run streamlit run frontend/app.py --server.port 8501
```
