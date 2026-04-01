"""
Bridge module — provides agent-level functions usable from backend routes.
Duplicates the SCIL mapping logic from the agent service so that the backend
can compute results without calling the agent service over the network.
"""

COMPETENCY_SCIL_MAP: dict[str, list[tuple[str, str, float]]] = {
    "persuasion": [
        ("sensus", "conviction", 0.40),
        ("lingua", "eloquence", 0.30),
        ("corpus", "gesture", 0.30),
    ],
    "analytical_thinking": [
        ("intellektus", "analytics", 0.50),
        ("intellektus", "structure", 0.30),
        ("intellektus", "objectivity", 0.20),
    ],
    "empathy": [
        ("sensus", "emotionality", 0.40),
        ("sensus", "inner_presence", 0.35),
        ("corpus", "facial_expression", 0.25),
    ],
    "presence": [
        ("corpus", "spatial_presence", 0.40),
        ("corpus", "appearance", 0.30),
        ("lingua", "voice", 0.30),
    ],
    "strategic_thinking": [
        ("intellektus", "goal_orientation", 0.40),
        ("intellektus", "analytics", 0.30),
        ("intellektus", "structure", 0.30),
    ],
    "storytelling": [
        ("lingua", "imagery", 0.40),
        ("lingua", "eloquence", 0.30),
        ("sensus", "emotionality", 0.30),
    ],
    "team_leadership": [
        ("sensus", "moment_focus", 0.35),
        ("corpus", "spatial_presence", 0.35),
        ("intellektus", "goal_orientation", 0.30),
    ],
    "clarity": [
        ("lingua", "articulation", 0.35),
        ("intellektus", "structure", 0.35),
        ("intellektus", "objectivity", 0.30),
    ],
}


def map_to_scil(competency_scores: dict[str, float]) -> dict[str, dict[str, float]]:
    """Map 360° competency scores → SCIL 16-frequency scores."""
    scil: dict[str, dict[str, float]] = {
        "sensus": {}, "corpus": {}, "intellektus": {}, "lingua": {},
    }
    weights: dict[str, dict[str, float]] = {
        "sensus": {}, "corpus": {}, "intellektus": {}, "lingua": {},
    }

    for comp, score in competency_scores.items():
        for area, freq, w in COMPETENCY_SCIL_MAP.get(comp, []):
            scil[area].setdefault(freq, 0.0)
            weights[area].setdefault(freq, 0.0)
            scil[area][freq] += score * w
            weights[area][freq] += w

    for area in scil:
        for freq in scil[area]:
            total_w = weights[area].get(freq, 1.0)
            if total_w > 0:
                scil[area][freq] = round(scil[area][freq] / total_w, 1)

    return scil


def compute_feedback_results(self_scores, other_scores_list):
    """Placeholder for full agent-based result computation."""
    pass
