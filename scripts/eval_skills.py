import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.app.video_score_generator import run_video_file_viral_score_pipeline


def _find_videos(root: Path) -> List[Path]:
    items = []
    for ext in ("*.mp4", "*.mov", "*.avi", "*.mkv"):
        items.extend(root.glob(ext))
    return sorted({p.resolve() for p in items})


async def _eval_one(video: Path) -> Dict[str, Any]:
    result = await run_video_file_viral_score_pipeline(video_path=str(video))
    data = result.model_dump()
    return {
        "video": str(video),
        "overall_score": data.get("overall_score"),
        "hook": data.get("hook_strength", {}).get("score"),
        "completion": data.get("completion_rate", {}).get("score"),
        "quality_flags": data.get("quality_flags"),
        "transcript_source": data.get("transcript_source"),
        "ocr_lines": data.get("ocr_text_lines"),
        "breakdowns": {
            "hook": data.get("hook_breakdown"),
            "retention": data.get("retention_breakdown"),
            "engagement": data.get("engagement_breakdown"),
            "trend": data.get("trend_breakdown"),
            "visual": data.get("visual_breakdown"),
            "audio": data.get("audio_breakdown"),
            "shareability": data.get("shareability_breakdown"),
        },
    }


async def main() -> None:
    root = Path(os.getenv("EVAL_VIDEO_DIR", "samples")).resolve()
    if not root.exists():
        root = Path(".").resolve()

    videos = _find_videos(root)
    if not videos:
        default = Path("sample.mp4").resolve()
        if default.exists():
            videos = [default]

    report: Dict[str, Any] = {
        "root": str(root),
        "count": len(videos),
        "items": [],
    }

    for video in videos:
        report["items"].append(await _eval_one(video))

    out_dir = Path(os.getenv("EVAL_REPORT_DIR", "reports")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "eval_report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(out_path))


if __name__ == "__main__":
    asyncio.run(main())
