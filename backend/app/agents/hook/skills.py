from backend.app.schemas.scoring import AgentSkillScore


CURIOUS_TERMS = {
    "?",
    "why",
    "how",
    "secret",
    "mistake",
    "nobody",
    "hidden",
    "watch",
    "before",
    "after",
}

EMOTION_TERMS = {
    "shock",
    "shocking",
    "hate",
    "love",
    "afraid",
    "fear",
    "embarrassing",
    "expensive",
    "waste",
    "wrong",
    "stop",
    "never",
}

CTA_TERMS = {
    "save",
    "share",
    "comment",
    "follow",
    "reply",
    "download",
    "try",
    "send",
}

OPENING_FILLER = {
    "hi",
    "hello",
    "hey guys",
    "welcome",
    "today i want",
    "in this video",
}


def _clamp(score: int) -> int:
    return max(0, min(100, score))


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _contains_number(text: str) -> bool:
    return any(char.isdigit() for char in text)


def _skill(score: int, reason: str, suggestions: list[str]) -> AgentSkillScore:
    return AgentSkillScore(score=_clamp(score), reason=reason, suggestions=suggestions)


def _pattern_name(text: str) -> str:
    if _contains_any(text, {"stop", "never", "mistake", "wrong"}):
        return "warning"
    if _contains_any(text, {"secret", "hidden", "nobody"}):
        return "secret"
    if "?" in text or text.startswith(("why", "how", "what")):
        return "question"
    if _contains_number(text):
        return "numbered_promise"
    return "generic_statement"


def build_hook_skills(
    *,
    text: str,
    niche: str | None,
    audience: str | None,
    hook_intensity: float,
    pacing_rate: float,
    frame_count: int,
) -> dict[str, AgentSkillScore]:
    normalized = (text or "").strip().lower()
    words = normalized.split()
    word_count = len(words)
    has_text = bool(normalized and normalized != "transcript was not provided.")
    has_number = _contains_number(normalized)
    has_question = "?" in normalized or normalized.startswith(("why", "how", "what"))
    has_curiosity = _contains_any(normalized, CURIOUS_TERMS) or has_question
    has_emotion = _contains_any(normalized, EMOTION_TERMS)
    has_cta = _contains_any(normalized, CTA_TERMS)
    has_filler = _contains_any(normalized[:60], OPENING_FILLER)
    niche_terms = [term for term in (niche or "").lower().split() if len(term) > 2]
    audience_terms = [term for term in (audience or "").lower().split() if len(term) > 2]
    names_viewer = any(term in normalized for term in niche_terms + audience_terms)

    scroll_stop_score = 52 + int(min(hook_intensity, 20) * 1.3) + int(min(pacing_rate, 3) * 8)
    if frame_count >= 9:
        scroll_stop_score += 8
    if has_number or has_question or has_emotion:
        scroll_stop_score += 8

    specificity_score = 52
    if has_text:
        specificity_score += 10
    if has_number:
        specificity_score += 15
    if names_viewer:
        specificity_score += 12
    if 5 <= word_count <= 16:
        specificity_score += 8

    curiosity_score = 62 if has_curiosity else 48
    if has_question:
        curiosity_score += 10
    if _contains_any(normalized, {"before", "after", "secret", "mistake"}):
        curiosity_score += 10

    emotion_score = 58 if has_emotion else 46
    if has_emotion and has_text:
        emotion_score += 14
    if _contains_any(normalized, {"you", "your"}):
        emotion_score += 6

    audience_fit_score = 55 + (18 if names_viewer else 0) + (8 if niche else 0) + (8 if audience else 0)

    cta_score = 50 + (22 if has_cta else 0) + (8 if has_question else 0)

    pattern = _pattern_name(normalized)
    pattern_score = {
        "warning": 78,
        "secret": 76,
        "question": 74,
        "numbered_promise": 72,
        "generic_statement": 54,
    }[pattern]
    if hook_intensity >= 8:
        pattern_score += 6

    retention_score = round(
        curiosity_score * 0.30
        + emotion_score * 0.20
        + specificity_score * 0.25
        + scroll_stop_score * 0.25
    )

    rewrite_score = 70 if has_text else 45
    if has_filler:
        rewrite_score -= 10

    sound_pacing_score = 55 + int(min(pacing_rate, 3) * 11)
    if hook_intensity >= 8:
        sound_pacing_score += 8

    structure_score = 58
    if not has_filler:
        structure_score += 10
    if has_question or has_number:
        structure_score += 10
    if 6 <= word_count <= 14:
        structure_score += 10

    visual_hook_score = 54 + int(min(hook_intensity, 20) * 1.5) + int(min(pacing_rate, 3) * 7)
    if frame_count >= 9:
        visual_hook_score += 6

    curiosity_gap = _skill(
        curiosity_score,
        "Measures whether the opening creates an unresolved question or information gap.",
        ["Delay the explanation by one beat after stating the tension."],
    )
    visual_hook = _skill(
        visual_hook_score,
        "Measures whether the sampled opening frames create immediate visual contrast or motion.",
        ["Use a cut, zoom, reveal, or bold overlay inside the first second."],
    )

    return {
        "scroll_stop": _skill(
            scroll_stop_score,
            "Scores first-second stopping power from frame samples, motion, pacing, and hook language.",
            ["Put the strongest visual contrast and clearest promise in the first frame."],
        ),
        "specificity": _skill(
            specificity_score,
            "Scores whether the hook names a concrete viewer, outcome, mistake, number, or situation.",
            ["Replace generic setup with one specific result, audience, or measurable claim."],
        ),
        "curiosity": curiosity_gap,
        "emotion": _skill(
            emotion_score,
            "Scores whether the opener carries stakes such as loss, surprise, pride, fear, or relief.",
            ["Name what the viewer risks losing or gains by watching."],
        ),
        "audience_fit": _skill(
            audience_fit_score,
            "Scores whether the hook clearly belongs to the supplied niche and target audience.",
            ["Call out the target viewer or their exact situation in the opening line."],
        ),
        "cta_engagement": _skill(
            cta_score,
            "Scores whether the hook creates an early comment, save, share, or follow pathway.",
            ["Add one low-friction prompt tied to the hook, such as save this or comment your version."],
        ),
        "pattern_match": _skill(
            pattern_score,
            f"Detected a {pattern} hook pattern from the script and opening signals.",
            ["Lean fully into one proven pattern instead of mixing several weak openings."],
        ),
        "retention_predictor": _skill(
            retention_score,
            "Predicts early retention from curiosity, emotion, specificity, and visual stop power.",
            ["Preview the payoff immediately, then withhold the key detail until after the hook."],
        ),
        "rewrite": _skill(
            rewrite_score,
            "Scores how much the current hook wording would benefit from rewrite variants.",
            [
                "Variant: Start with the costly mistake, then reveal the fix.",
                "Variant: Start with a numbered promise for the exact viewer.",
            ],
        ),
        "sound_pacing": _skill(
            sound_pacing_score,
            "Scores whether the opening pace appears energetic enough for a short-form hook.",
            ["Align the first visual change with the first beat or spoken stress."],
        ),
        "structure": _skill(
            structure_score,
            "Scores whether the hook avoids slow intros and uses a compact question, claim, or tension.",
            ["Remove greetings and setup; open directly on the claim or problem."],
        ),
        "visual_hook": visual_hook,
        "curiosity_gap": curiosity_gap,
        "visual_disruption": visual_hook,
    }
