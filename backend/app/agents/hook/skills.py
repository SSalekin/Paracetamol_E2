from backend.app.schemas.scoring import AgentSkillScore


def build_hook_skills(
    *,
    scroll_stop_score: int,
    specificity_score: int,
    curiosity_score: int,
    visual_disruption_score: int,
) -> dict[str, AgentSkillScore]:
    return {
        "scroll_stop": AgentSkillScore(
            score=scroll_stop_score,
            reason="Estimated from available first-three-second frame samples.",
            suggestions=["Keep the strongest visual contrast in the first frame."],
        ),
        "specificity": AgentSkillScore(
            score=specificity_score,
            reason="Estimated from whether usable transcript/script context exists.",
            suggestions=["Name the specific outcome or target viewer immediately."],
        ),
        "curiosity_gap": AgentSkillScore(
            score=curiosity_score,
            reason="Estimated from script/question/curiosity trigger terms.",
            suggestions=["Open a clear information gap before explaining."],
        ),
        "visual_disruption": AgentSkillScore(
            score=visual_disruption_score,
            reason="Estimated from OpenCV motion and scene-cut features.",
            suggestions=["Add a pattern break in the first second if the opening is static."],
        ),
    }
