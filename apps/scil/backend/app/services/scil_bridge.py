"""SCIL Bridge — Competency-to-SCIL-Frequency mapping.

Ported from gr8hub/backend/app/agents_bridge.py.
Maps 8 competencies to 16 SCIL frequencies for 360-degree feedback integration.
"""

COMPETENCY_SCIL_MAP: dict[str, list[tuple[str, str, float]]] = {
    "persuasion": [
        ("sensus", "innere_ueberzeugung", 0.40),
        ("lingua", "beredsamkeit", 0.30),
        ("corpus", "gestik", 0.30),
    ],
    "analytical_thinking": [
        ("intellektus", "analytik", 0.50),
        ("intellektus", "struktur", 0.30),
        ("intellektus", "sachlichkeit", 0.20),
    ],
    "empathy": [
        ("sensus", "emotionalitaet", 0.40),
        ("sensus", "innere_praesenz", 0.35),
        ("corpus", "mimik", 0.25),
    ],
    "presence": [
        ("corpus", "raeumliche_praesenz", 0.40),
        ("corpus", "erscheinungsbild", 0.30),
        ("lingua", "stimme", 0.30),
    ],
    "strategic_thinking": [
        ("intellektus", "zielorientierung", 0.40),
        ("intellektus", "analytik", 0.30),
        ("intellektus", "struktur", 0.30),
    ],
    "storytelling": [
        ("lingua", "bildhaftigkeit", 0.40),
        ("lingua", "beredsamkeit", 0.30),
        ("sensus", "emotionalitaet", 0.30),
    ],
    "team_leadership": [
        ("sensus", "prozessfokussierung", 0.35),
        ("corpus", "raeumliche_praesenz", 0.35),
        ("intellektus", "zielorientierung", 0.30),
    ],
    "clarity": [
        ("lingua", "artikulation", 0.35),
        ("intellektus", "struktur", 0.35),
        ("intellektus", "sachlichkeit", 0.30),
    ],
}


def map_to_scil(competency_scores: dict[str, float]) -> dict[str, dict[str, float]]:
    """Map 360 competency scores to SCIL 16-frequency scores."""
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
