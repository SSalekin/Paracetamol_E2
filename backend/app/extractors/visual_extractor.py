import base64
import cv2
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class VideoFrameExtractionError(ValueError):
    pass


class VideoTranscodeError(ValueError):
    pass


def _encode_frame_to_b64(frame, jpeg_quality: int = 60) -> str:
    frame = cv2.resize(frame, (480, 854))

    ok, buffer = cv2.imencode(
        ".jpg",
        frame,
        [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
    )

    if not ok:
        raise VideoFrameExtractionError("Could not encode frame as JPEG.")

    return base64.b64encode(buffer).decode("utf-8")


def _transcode_first_seconds_to_h264(video_path: str, seconds: int = 4) -> str:
    if not shutil.which("ffmpeg"):
        raise VideoTranscodeError(
            "OpenCV could not decode this video and ffmpeg is not installed."
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
        str(seconds),
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

    result = subprocess.run(command, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        if os.path.exists(output_path):
            os.unlink(output_path)
        raise VideoTranscodeError(result.stderr.strip() or "ffmpeg transcode failed.")

    return output_path


def extract_hook_frames(video_path: str, seconds: int = 3, frames_per_second: int = 1) -> list[str]:
    path = Path(video_path)

    if not path.exists():
        raise VideoFrameExtractionError(f"Video file does not exist: {video_path}")

    cap = cv2.VideoCapture(str(path))

    if not cap.isOpened():
        raise VideoFrameExtractionError("Could not open uploaded video file.")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)

        target_indices: list[int] = []

        for second in range(seconds):
            for sample in range(frames_per_second):
                offset = int((sample / frames_per_second) * fps)
                target_indices.append(int(second * fps) + offset)

        frames_b64: list[str] = []

        for frame_index in target_indices:
            if frame_count and frame_index >= frame_count:
                continue

            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = cap.read()

            if not ok:
                continue

            frames_b64.append(_encode_frame_to_b64(frame))

        if not frames_b64:
            raise VideoFrameExtractionError("No frames could be extracted.")

        return frames_b64

    finally:
        cap.release()


def extract_visual_features(video_path: str, analysis_seconds: float = 4.0) -> dict[str, Any]:
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise VideoFrameExtractionError("Could not open video for visual features.")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        duration = frame_count / fps if frame_count else 0.0

        max_frames = int(fps * analysis_seconds)

        previous_gray = None
        diffs: list[float] = []
        scene_cut_count = 0

        threshold = 35.0

        for _ in range(max_frames):
            ok, frame = cap.read()

            if not ok:
                break

            small = cv2.resize(frame, (160, 90))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

            if previous_gray is not None:
                diff = cv2.absdiff(previous_gray, gray)
                mean_diff = float(diff.mean())
                diffs.append(mean_diff)

                if mean_diff > threshold:
                    scene_cut_count += 1

            previous_gray = gray

        hook_intensity = sum(diffs) / len(diffs) if diffs else 0.0
        pacing_rate = scene_cut_count / analysis_seconds if analysis_seconds else 0.0

        return {
            "duration_seconds": round(duration, 2),
            "analysis_window_seconds": analysis_seconds,
            "hook_intensity": round(hook_intensity, 2),
            "scene_cut_count": scene_cut_count,
            "pacing_rate": round(pacing_rate, 2),
        }

    finally:
        cap.release()


def extract_visual_package(video_path: str) -> dict[str, Any]:
    try:
        return {
            "hook_frames_b64": extract_hook_frames(
                video_path,
                seconds=3,
                frames_per_second=1,
            ),
            "visual_features": extract_visual_features(
                video_path,
                analysis_seconds=4.0,
            ),
        }
    except VideoFrameExtractionError:
        transcoded_path = None

        try:
            transcoded_path = _transcode_first_seconds_to_h264(video_path, seconds=4)

            return {
                "hook_frames_b64": extract_hook_frames(
                    transcoded_path,
                    seconds=3,
                    frames_per_second=1,
                ),
                "visual_features": extract_visual_features(
                    transcoded_path,
                    analysis_seconds=4.0,
                ),
            }
        finally:
            if transcoded_path and os.path.exists(transcoded_path):
                os.unlink(transcoded_path)
