import asyncio
import time
from typing import Any

from backend.app.extractors.visual_extractor import extract_visual_package
from backend.app.extractors.transcript_extractor import extract_text_script
from backend.app.extractors.context_extractor import extract_context
from backend.app.agents.hook import run_hook_agent
from backend.app.agents.retention import run_retention_agent
from backend.app.agents.share_save import run_share_save_agent
from backend.app.agents.seo import run_seo_agent
from backend.app.agents.trend import run_trend_agent
from backend.app.agents.niche_fit import run_niche_fit_agent
from backend.app.agents.engagement import run_engagement_agent
from backend.app.agents.final_scorer import run_final_scorer_agent
from backend.app.schemas.graph_state import VideoScoreGraphState
from backend.app.core.aggregator import aggregate_score


async def extractor_node(state: VideoScoreGraphState) -> dict[str, Any]:
    debug_trace = list(state.get("debug_trace", []))
    debug_trace.append("extractor:start")
    started = time.perf_counter()

    visual_package = await asyncio.to_thread(
        extract_visual_package,
        state["video_path"],
    )

    text_script = extract_text_script(
        provided_transcript=state.get("full_transcript"),
        fallback_text=state.get("trend_context", ""),
    )

    context_package = extract_context(
        trend_context=state.get("trend_context"),
        niche=state.get("niche", "General short-form content"),
        audience=state.get("audience", "General social media audience"),
    )

    debug_trace.append(
        f"extractor:visual_features={visual_package['visual_features']}"
    )
    debug_trace.append(f"extractor:duration={time.perf_counter() - started:.2f}s")
    debug_trace.append("extractor:complete")

    return {
        **visual_package,
        "text_script": text_script,
        **context_package,
        "debug_trace": debug_trace,
    }

async def agents_node(state: VideoScoreGraphState) -> dict[str, Any]:
    debug_trace = list(state.get("debug_trace", []))
    debug_trace.append("agents:start")
    started = time.perf_counter()

    results = await asyncio.gather(
        run_hook_agent(dict(state)),
        run_retention_agent(dict(state)),
        run_share_save_agent(dict(state)),
        run_trend_agent(dict(state)),
        run_seo_agent(dict(state)),
        run_engagement_agent(dict(state)),
        run_niche_fit_agent(dict(state)),
    )

    agent_results = {
        result.name: result.model_dump()
        for result in results
    }

    for result in results:
        debug_trace.append(f"agents:{result.name}={result.score}")

    debug_trace.append(f"agents:duration={time.perf_counter() - started:.2f}s")
    debug_trace.append("agents:complete")

    return {
        "agent_results": agent_results,
        "debug_trace": debug_trace,
    }

async def aggregator_node(state: VideoScoreGraphState) -> dict[str, Any]:
    debug_trace = list(state.get("debug_trace", []))
    debug_trace.append("aggregator:start")
    started = time.perf_counter()

    try:
        final_score = await run_final_scorer_agent({**state, "debug_trace": debug_trace})
        final_score.debug_trace.append("aggregator:llm_final_scorer")
    except Exception as exc:
        debug_trace.append(f"aggregator:llm_final_scorer_failed={exc}")
        final_score = aggregate_score({**state, "debug_trace": debug_trace})

    final_score.debug_trace.append(f"aggregator:duration={time.perf_counter() - started:.2f}s")

    return {
        "final_score": final_score,
        "debug_trace": final_score.debug_trace,
    }
