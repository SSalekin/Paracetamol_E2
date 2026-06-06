from pydantic import BaseModel

from backend.app.core.graph import viral_score_graph
from backend.app.extractors.visual_extractor import VideoFrameExtractionError
from backend.app.schemas.scoring import ViralScoreResponse


class VideoScorePipelineInput(BaseModel):
    video_path: str
    niche: str = "General short-form content"
    audience: str = "General social media audience"
    posting_time: str = "Not specified"
    full_transcript: str = "Transcript was not provided."
    trend_context: str = "Live audio and keyword trend context was not provided."


async def run_video_file_viral_score_pipeline(
    video_path: str,
    niche: str = "General short-form content",
    audience: str = "General social media audience",
    posting_time: str = "Not specified",
    full_transcript: str = "Transcript was not provided.",
    trend_context: str = "Live audio and keyword trend context was not provided.",
) -> ViralScoreResponse:
    pipeline_input = VideoScorePipelineInput(
        video_path=video_path,
        niche=niche,
        audience=audience,
        posting_time=posting_time,
        full_transcript=full_transcript,
        trend_context=trend_context,
    )

    final_state = await viral_score_graph.ainvoke(
        {
            **pipeline_input.model_dump(),
            "debug_trace": [],
        }
    )

    return final_state["final_score"]
