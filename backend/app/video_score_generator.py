import os
import asyncio
import base64
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

import cv2
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI  # Dola Seed 2.0 Lite uses the OpenAI-compatible SDK
from langgraph.graph import END, START, StateGraph

for parent in Path(__file__).resolve().parents:
    env_path = parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        break

# =====================================================================
# 1. DEFINE RIGID PYDANTIC SCHEMAS FOR THE 7-DIMENSION ANALYTICS
# =====================================================================

class DimensionScore(BaseModel):
    score: int = Field(..., description="Score from 0 to 100", ge=0, le=100)
    explanation: str = Field(..., description="Brutally honest analytical insight explaining the score.")
    actionable_fix: str = Field(..., description="Concrete, explicit visual or structural change to make right now.")

class RetentionDropZone(BaseModel):
    timestamp_range: str = Field(..., description="Timestamp range where dropoff is critical, e.g., '00:12 - 00:15'")
    reason: str = Field(..., description="Why viewers are highly likely to swipe away here.")
    severity: str = Field(..., description="High, Medium, or Low risk factor.")

class ViralScoreResponse(BaseModel):
    overall_score: int = Field(..., description="Aggregated mathematical score from 0-100.", ge=0, le=100)

    # The 7 Demanded Dimensions
    hook_strength: DimensionScore = Field(..., description="Dimension 1: Focuses on the first 3 seconds.")
    completion_rate: DimensionScore = Field(..., description="Dimension 2: Focuses on holding attention to the final frame.")
    shares_saves_probability: DimensionScore = Field(..., description="Dimension 3: Value-metrics over passive likes.")
    sound_trend_timing: DimensionScore = Field(..., description="Dimension 4: Matching audio waves to momentum.")
    search_keyword_relevance: DimensionScore = Field(..., description="Dimension 5: SEO and search discoverability layout.")
    early_engagement_velocity: DimensionScore = Field(..., description="Dimension 6: Initial algorithmic test group trigger capacity.")
    content_niche_fit: DimensionScore = Field(..., description="Dimension 7: Integrity regarding baseline brand targets.")

    # Required Scenarios Outputs
    retention_drop_zones: List[RetentionDropZone] = Field(..., description="List of visual or spoken drop zones in the video timeline.")
    predicted_reach_range: str = Field(..., description="Estimated reach interval, e.g., '5,000 - 15,000 views' with confidence interval.")
    suggested_script_variant: Optional[str] = Field(None, description="Bonus: Automated script variation optimized to resolve identified flaws.")


class VideoScorePipelineInput(BaseModel):
    video_path: str
    niche: str = "General short-form content"
    audience: str = "General social media audience"
    posting_time: str = "Not specified"
    full_transcript: str = "Transcript was not provided."
    trend_context: str = "Live audio and keyword trend context was not provided."


class VideoScoreGraphState(TypedDict, total=False):
    video_path: str
    niche: str
    audience: str
    posting_time: str
    full_transcript: str
    trend_context: str
    hook_frames_b64: List[str]
    body_frames_b64: List[str]
    viral_score: ViralScoreResponse


class VideoFrameExtractionError(ValueError):
    pass


class VideoTranscodeError(ValueError):
    pass

# =====================================================================
# 2. INITIALIZE DOLA SEED 2.0 LITE WITH STRUCTURED OUTPUT
# =====================================================================

# Get Endpoint Base URL and API Key from BytePlus/ModelArk console variables
DOLA_API_KEY = os.getenv("DOLA_API_KEY", "your_byteplus_ark_api_key_here")
DOLA_BASE_URL = os.getenv("DOLA_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3") # Or your assigned region base endpoint

llm = ChatOpenAI(
    model="seed-2-0-lite-260428",
    api_key=DOLA_API_KEY,
    base_url=DOLA_BASE_URL,
    temperature=0.1
)

# =====================================================================
# 3. BUILD THE CORE ANALYTICAL PROMPT LAYER
# =====================================================================

VIRAL_ANALYSIS_SYSTEM_PROMPT = """You are the underlying core evaluation brain of the ViralScore engine for the AI Hackathon 2026.
Your job is to act as an elite TikTok growth master, inspecting content PRE-PUBLICATION.
You evaluate videos against strict algorithmic constraints where the completion threshold is now 70%.

You will receive:
1. Ground truth context parameters (Niche, Audience, Planned Post Time).
2. Complete video transcript, when available.
3. Live audio trend/keyword context, when available.
4. Base64 images sampled from the first 3 seconds:
   - Image 1-9: High-velocity sampling of the first 3 seconds (Hook).

CRITICAL EVALUATION ENGINE CRITERIA:
- Hook Strength: Analyze visual disrupt/overlays in Images 1-9 alongside opening script strings. Deduct points for generic introductions.
- Completion Rate: Identify drop zones. Check for 'outro drop-off traps' where verbal cues signaling the end of the video appear too early.
- Sound Trend/Search: Cross-reference the extracted soundtrack data with the Live Trend Context payload when provided. If not provided, say the score is based on visual hook evidence only.
- Actionable Fixes: Every fix must be concrete. Never use generic advice like 'make it more engaging'. Tell them exactly where to cut, what text to overlay, or what words to speak.

Return only valid JSON matching this exact object shape:
{
  "overall_score": 0,
  "hook_strength": {"score": 0, "explanation": "", "actionable_fix": ""},
  "completion_rate": {"score": 0, "explanation": "", "actionable_fix": ""},
  "shares_saves_probability": {"score": 0, "explanation": "", "actionable_fix": ""},
  "sound_trend_timing": {"score": 0, "explanation": "", "actionable_fix": ""},
  "search_keyword_relevance": {"score": 0, "explanation": "", "actionable_fix": ""},
  "early_engagement_velocity": {"score": 0, "explanation": "", "actionable_fix": ""},
  "content_niche_fit": {"score": 0, "explanation": "", "actionable_fix": ""},
  "retention_drop_zones": [{"timestamp_range": "", "reason": "", "severity": ""}],
  "predicted_reach_range": "",
  "suggested_script_variant": ""
}"""


def _build_user_text(
    niche: str,
    audience: str,
    posting_time: str,
    full_transcript: str,
    trend_context: str,
) -> str:
    return f"""--- METADATA & DATA PIPELINES ---
Target Niche: {niche}
Target Audience: {audience}
Planned Posting Time: {posting_time}
Full Video Transcript: '{full_transcript}'
Live Audio/Keyword Trend Context: {trend_context}

Please evaluate the provided chronological visual frames against this data framework.
Only score what can be inferred from the supplied frames and metadata."""


def _image_payload_from_base64(frames_b64: List[str]) -> List[Dict[str, Any]]:
    return [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
        }
        for img_b64 in frames_b64
    ]


def _extract_frames_with_opencv(video_path: str) -> List[str]:
    """
    Extract the first 3 frames from each of the first 3 seconds: 0s, 1s, and 2s.
    Returns up to 9 JPEG base64 strings in chronological order.
    """
    path = Path(video_path)
    if not path.exists():
        raise VideoFrameExtractionError(f"Video file does not exist: {video_path}")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise VideoFrameExtractionError("Could not open uploaded video file.")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0:
            fps = 30.0

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        target_indices: List[int] = []
        for second in range(3):
            second_start = int(round(second * fps))
            target_indices.extend(second_start + offset for offset in range(3))

        frames_b64: List[str] = []
        for frame_index in target_indices:
            if frame_count and frame_index >= frame_count:
                continue

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = cap.read()
            if not ok:
                continue

            ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if not ok:
                continue

            frames_b64.append(base64.b64encode(buffer).decode("utf-8"))

        if not frames_b64:
            raise VideoFrameExtractionError("No frames could be extracted from the uploaded video.")

        return frames_b64
    finally:
        cap.release()


def _transcode_first_three_seconds_to_h264(video_path: str) -> str:
    if not shutil.which("ffmpeg"):
        raise VideoTranscodeError(
            "Uploaded video appears to use a codec OpenCV cannot decode, and ffmpeg is not installed. "
            "Install ffmpeg with HEVC support or upload an H.264 MP4."
        )

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    output_path = output.name
    output.close()

    command = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        video_path,
        "-t",
        "3",
        "-map",
        "0:v:0",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError as exc:
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise VideoTranscodeError(f"Could not run ffmpeg: {exc}") from exc

    if result.returncode != 0:
        if os.path.exists(output_path):
            os.unlink(output_path)
        stderr = result.stderr.strip() or "ffmpeg could not transcode the uploaded video."
        raise VideoTranscodeError(stderr)

    return output_path


def _extract_first_three_seconds_frames(video_path: str) -> List[str]:
    """
    Extract hook frames directly with OpenCV. If OpenCV cannot decode the input
    codec, transcode the first 3 seconds to H.264 and retry. This supports common
    HEVC/H.265 MP4 uploads from iPhone and Android devices.
    """
    try:
        return _extract_frames_with_opencv(video_path)
    except VideoFrameExtractionError as first_error:
        transcoded_path = None
        try:
            transcoded_path = _transcode_first_three_seconds_to_h264(video_path)
            return _extract_frames_with_opencv(transcoded_path)
        except VideoTranscodeError as transcode_error:
            raise VideoFrameExtractionError(str(transcode_error)) from transcode_error
        except VideoFrameExtractionError as retry_error:
            raise VideoFrameExtractionError(
                f"{first_error} Retried after transcoding, but frame extraction still failed: {retry_error}"
            ) from retry_error
        finally:
            if transcoded_path and os.path.exists(transcoded_path):
                os.unlink(transcoded_path)


async def _extract_frames_step(payload: Dict[str, Any]) -> Dict[str, Any]:
    frames_b64 = await asyncio.to_thread(_extract_first_three_seconds_frames, payload["video_path"])
    return {**payload, "hook_frames_b64": frames_b64, "body_frames_b64": []}


async def _score_frames_step(payload: Dict[str, Any]) -> ViralScoreResponse:
    return await run_viral_score_pipeline(
        niche=payload["niche"],
        audience=payload["audience"],
        posting_time=payload["posting_time"],
        full_transcript=payload["full_transcript"],
        trend_context=payload["trend_context"],
        hook_frames_b64=payload["hook_frames_b64"],
        body_frames_b64=payload.get("body_frames_b64", []),
    )


async def _score_frames_node(state: VideoScoreGraphState) -> Dict[str, ViralScoreResponse]:
    score = await _score_frames_step(state)
    return {"viral_score": score}


def _build_video_score_graph():
    graph = StateGraph(VideoScoreGraphState)
    graph.add_node("extract_hook_frames", _extract_frames_step)
    graph.add_node("score_frames", _score_frames_node)
    graph.add_edge(START, "extract_hook_frames")
    graph.add_edge("extract_hook_frames", "score_frames")
    graph.add_edge("score_frames", END)
    return graph.compile()


# LangGraph orchestrates the video scoring workflow; LangChain handles model calls.
video_file_viral_score_graph = _build_video_score_graph()

# =====================================================================
# 4. ASYNC ORCHESTRATION PIPELINE FOR THE FASTAPI ROUTER LAYER
# =====================================================================

async def run_viral_score_pipeline(
    niche: str,
    audience: str,
    posting_time: str,
    full_transcript: str,
    trend_context: str,
    hook_frames_b64: List[str],  # 9 frames from first 3 seconds
    body_frames_b64: List[str]   # sampled frames from remainder of video
) -> ViralScoreResponse:
    """
    Orchestrates data packaging and invokes the LangChain LCEL pipe asynchronously.
    """

    user_content = [
        {
            "type": "text",
            "text": _build_user_text(
                niche=niche,
                audience=audience,
                posting_time=posting_time,
                full_transcript=full_transcript,
                trend_context=trend_context,
            ),
        },
        *_image_payload_from_base64(hook_frames_b64 + body_frames_b64),
    ]

    response = await llm.ainvoke([
        SystemMessage(content=VIRAL_ANALYSIS_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ])

    raw_content = getattr(response, "content", response)
    if not isinstance(raw_content, str):
        raw_content = str(raw_content)

    text = raw_content.strip()
    if "```" in text:
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise RuntimeError("LLM response did not contain a JSON object.")

    payload = json.loads(text[start : end + 1])
    return ViralScoreResponse.model_validate(payload)


async def run_video_file_viral_score_pipeline(
    video_path: str,
    niche: str = "General short-form content",
    audience: str = "General social media audience",
    posting_time: str = "Not specified",
    full_transcript: str = "Transcript was not provided.",
    trend_context: str = "Live audio and keyword trend context was not provided.",
) -> ViralScoreResponse:
    """
    Orchestrates video upload scoring: OpenCV frame extraction, multimodal packaging,
    and Dola Seed 2.0 Lite scoring.
    """
    pipeline_input = VideoScorePipelineInput(
        video_path=video_path,
        niche=niche,
        audience=audience,
        posting_time=posting_time,
        full_transcript=full_transcript,
        trend_context=trend_context,
    )
    final_state = await video_file_viral_score_graph.ainvoke(pipeline_input.model_dump())
    return final_state["viral_score"]

# =====================================================================
# 5. LOCAL VERIFICATION BLOCK
# =====================================================================
if __name__ == "__main__":
    async def test_main():
        # Minimal blank base64 payload representing frames generated out of OpenCV
        mock_frame = base64.b64encode(b"fakedata").decode("utf-8")

        print("🚀 Invoking Dola Seed 2.0 Lite evaluation engine...")
        try:
            result = await run_viral_score_pipeline(
                niche="E-commerce Fashion",
                audience="Cat Lovers, Gen Z impulsive buyers",
                posting_time="8:00 PM Vietnam Time",
                full_transcript="Look at this cat t-shirt it is so cool buy it now link in bio.",
                trend_context="Trending Sounds: ['Espresso Remix' Status: Peaked 3 days ago]",
                hook_frames_b64=[mock_frame] * 9,
                body_frames_b64=[mock_frame] * 5
            )
            print("\n✅ Matrix Generation Complete:")
            print(result.model_dump_json(indent=2))
        except Exception as e:
            print(f"❌ Pipeline Failure: {e}")

    # asyncio.run(test_main())
