import os
import shutil
import tempfile
import logging
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from backend.app.video_score_generator import (
    ViralScoreResponse,
    VideoFrameExtractionError,
    run_video_file_viral_score_pipeline,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TeamParacetamol API",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "message": "Hello from FastAPI!"
    }


@app.post("/score-video", response_model=ViralScoreResponse)
async def score_video(
    video: UploadFile = File(...),
    niche: str = Form("General short-form content"),
    audience: str = Form("General social media audience"),
    posting_time: str = Form("Not specified"),
    full_transcript: Optional[str] = Form(None),
    trend_context: Optional[str] = Form(None),
):
    content_type = video.content_type or ""
    if content_type and not content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a video.")

    suffix = os.path.splitext(video.filename or "")[1] or ".mp4"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_video:
            temp_path = temp_video.name
            shutil.copyfileobj(video.file, temp_video)

        return await run_video_file_viral_score_pipeline(
            video_path=temp_path,
            niche=niche,
            audience=audience,
            posting_time=posting_time,
            full_transcript=full_transcript or "Transcript was not provided.",
            trend_context=trend_context or "Live audio and keyword trend context was not provided.",
        )
    except VideoFrameExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        logger.exception("Video scoring configuration failure")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Video scoring failed")
        raise HTTPException(status_code=500, detail=f"Video scoring failed: {exc}") from exc
    finally:
        await video.close()
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
