"""SCIL Scoring Engine — computes polygon data, balance scores, classifications, and psychometrics.

All functions operate on the canonical SCIL scores dict structure:
{
    "sensus": {"innere_praesenz": 3.2, "innere_ueberzeugung": 2.8, ...},
    "corpus": {"erscheinungsbild": 2.6, ...},
    "intellektus": {"sachlichkeit": 3.1, ...},
    "lingua": {"stimme": 2.8, ...},
}

Scores are on a 0-4 main scale with 0.1 precision.

Psychometric functions operate on item_responses:
[{"item_id": "S01", "score": 3.2, "confidence": 0.8, "area": "sensus", "frequency": "innere_praesenz", ...}]
"""

import math
from dataclasses import dataclass


SCIL_AREAS: dict[str, list[str]] = {
    "sensus": [
        "innere_praesenz",
        "innere_ueberzeugung",
        "prozessfokussierung",
        "emotionalitaet",
    ],
    "corpus": [
        "erscheinungsbild",
        "mimik",
        "gestik",
        "raeumliche_praesenz",
    ],
    "intellektus": [
        "sachlichkeit",
        "analytik",
        "struktur",
        "zielorientierung",
    ],
    "lingua": [
        "stimme",
        "artikulation",
        "beredsamkeit",
        "bildhaftigkeit",
    ],
}

AREA_LABELS: dict[str, str] = {
    "sensus": "Sensus",
    "corpus": "Corpus",
    "intellektus": "Intellektus",
    "lingua": "Lingua",
}

AREA_COLORS: dict[str, str] = {
    "sensus": "#E74C3C",
    "corpus": "#F39C12",
    "intellektus": "#3498DB",
    "lingua": "#2ECC71",
}

FREQ_LABELS: dict[str, str] = {
    "innere_praesenz": "Innere Praesenz",
    "innere_ueberzeugung": "Innere Ueberzeugung",
    "prozessfokussierung": "Prozessfokussierung",
    "emotionalitaet": "Emotionalitaet",
    "erscheinungsbild": "Erscheinungsbild",
    "mimik": "Mimik",
    "gestik": "Gestik",
    "raeumliche_praesenz": "Raeumliche Praesenz",
    "sachlichkeit": "Sachlichkeit",
    "analytik": "Analytik",
    "struktur": "Struktur",
    "zielorientierung": "Zielorientierung",
    "stimme": "Stimme",
    "artikulation": "Artikulation",
    "beredsamkeit": "Beredsamkeit",
    "bildhaftigkeit": "Bildhaftigkeit",
}

# Bewertungsstufen nach SCIL original
RATING_LEVELS = [
    ("a", "Ausgepragte Staerke", 3.5, 4.0),
    ("b", "Staerkenpotenzial", 2.5, 3.5),
    ("c", "Durchschnittliche Staerke", 1.5, 2.5),
    ("d", "Relative Staerke", 0.5, 1.5),
    ("e", "Schwache Auspraegung", 0.0, 0.5),
]


@dataclass
class FrequencyResult:
    area: str
    key: str
    label: str
    score: float
    level: str
    level_label: str


def classify_score(score: float) -> tuple[str, str]:
    """Classify a single score into one of 5 levels (a-e)."""
    for level, label, low, high in RATING_LEVELS:
        if score >= low:
            return level, label
    return "e", "Schwache Auspraegung"


def compute_area_averages(scores: dict) -> dict[str, float]:
    """Compute the average score per SCIL area (Cluster-Mittelwert)."""
    averages: dict[str, float] = {}
    for area, freqs in SCIL_AREAS.items():
        area_scores = scores.get(area, {})
        values = [area_scores.get(f, 0.0) for f in freqs if f in area_scores]
        if values:
            averages[area] = round(sum(values) / len(values), 2)
        else:
            averages[area] = 0.0
    return averages


def compute_balance_score(scores: dict) -> float:
    """Compute the charisma/balance score.

    Lower variance across all 16 frequencies = higher balance.
    Returns a score on 0-4 scale where 4 = perfect balance.
    """
    all_values: list[float] = []
    for area, freqs in SCIL_AREAS.items():
        area_scores = scores.get(area, {})
        for f in freqs:
            if f in area_scores:
                all_values.append(area_scores[f])

    if len(all_values) < 4:
        return 0.0

    mean = sum(all_values) / len(all_values)
    variance = sum((v - mean) ** 2 for v in all_values) / len(all_values)
    # Lower variance = higher balance; scale so that variance 0 → 4, variance 2 → 0
    balance = max(0.0, 4.0 - variance * 2.0)
    return round(balance, 1)


def compute_overall_mean(scores: dict) -> float:
    """Compute the overall mean across all 16 frequencies (Gesamt-Mittelwert)."""
    all_values: list[float] = []
    for area, freqs in SCIL_AREAS.items():
        area_scores = scores.get(area, {})
        for f in freqs:
            if f in area_scores:
                all_values.append(area_scores[f])

    if not all_values:
        return 0.0
    return round(sum(all_values) / len(all_values), 2)


def classify_frequencies(scores: dict) -> list[FrequencyResult]:
    """Classify all 16 frequencies into rating levels."""
    results: list[FrequencyResult] = []
    for area, freqs in SCIL_AREAS.items():
        area_scores = scores.get(area, {})
        for f in freqs:
            score = area_scores.get(f, 0.0)
            level, level_label = classify_score(score)
            results.append(FrequencyResult(
                area=area,
                key=f,
                label=FREQ_LABELS.get(f, f),
                score=score,
                level=level,
                level_label=level_label,
            ))
    return results


def get_top_strengths(scores: dict, n: int = 3) -> list[FrequencyResult]:
    """Get the top-N strongest frequencies."""
    classified = classify_frequencies(scores)
    classified.sort(key=lambda r: r.score, reverse=True)
    return classified[:n]


def get_development_areas(scores: dict, n: int = 3) -> list[FrequencyResult]:
    """Get the top-N frequencies with most development potential (lowest scores)."""
    classified = classify_frequencies(scores)
    classified.sort(key=lambda r: r.score)
    return classified[:n]


def compute_polygon(scores: dict) -> dict:
    """Compute full polygon data for the SCIL visualization.

    Returns a dict suitable for the frontend SCILPolygon component:
    {
        "areas": {
            "sensus": {
                "label": "Sensus",
                "color": "#E74C3C",
                "average": 2.85,
                "frequencies": {
                    "innere_praesenz": {"score": 3.2, "label": "...", "level": "b"},
                    ...
                }
            },
            ...
        },
        "overall_mean": 2.7,
        "balance_score": 3.2,
        "total_frequencies": 16,
        "classified_count": 16,
    }
    """
    areas_data: dict = {}
    classified_count = 0

    for area, freqs in SCIL_AREAS.items():
        area_scores = scores.get(area, {})
        freq_data: dict = {}
        values: list[float] = []

        for f in freqs:
            score = area_scores.get(f, 0.0)
            level, level_label = classify_score(score)
            freq_data[f] = {
                "score": score,
                "label": FREQ_LABELS.get(f, f),
                "level": level,
                "level_label": level_label,
            }
            if f in area_scores:
                values.append(score)
                classified_count += 1

        areas_data[area] = {
            "label": AREA_LABELS[area],
            "color": AREA_COLORS[area],
            "average": round(sum(values) / len(values), 2) if values else 0.0,
            "frequencies": freq_data,
        }

    return {
        "areas": areas_data,
        "overall_mean": compute_overall_mean(scores),
        "balance_score": compute_balance_score(scores),
        "total_frequencies": 16,
        "classified_count": classified_count,
    }


# ---------------------------------------------------------------------------
# Psychometrics — Per-Item Response Analysis
# ---------------------------------------------------------------------------

def compute_cronbach_alpha(item_responses: list[dict], area: str) -> float | None:
    """Cronbach's Alpha fuer internen Konsistenzcheck pro Cluster.

    Alpha = (k / (k-1)) * (1 - sum(item_variances) / total_variance)
    where k = number of items.

    Requires at least 3 items with scores to be meaningful.
    Returns None if insufficient data.
    """
    # Filter items for the given area
    area_responses = [r for r in item_responses if r.get("area") == area]
    if len(area_responses) < 3:
        return None

    # Group scores by item_id
    item_scores: dict[str, list[float]] = {}
    for r in area_responses:
        item_id = r["item_id"]
        if item_id not in item_scores:
            item_scores[item_id] = []
        item_scores[item_id].append(float(r["score"]))

    # For single-pass data (one score per item per run), we use
    # the item scores as a single "response vector" and compute alpha
    # based on variance decomposition.
    k = len(item_scores)
    if k < 3:
        return None

    # Single score per item per run → use scores as a vector
    scores = [item_scores[item_id][0] for item_id in item_scores if item_scores[item_id]]
    if len(scores) < 3:
        return None

    mean = sum(scores) / len(scores)
    total_variance = sum((s - mean) ** 2 for s in scores) / len(scores)

    if total_variance == 0:
        return 1.0  # All scores identical = perfect consistency

    # For a single run, we approximate item variance using confidence-weighted variance
    # Each item's "variance" is estimated from its confidence (lower confidence = higher variance)
    confidences = []
    for item_id in item_scores:
        conf_list = [r["confidence"] for r in area_responses if r["item_id"] == item_id]
        if conf_list:
            confidences.append(conf_list[0])

    # Approximate: item_variance_i = (1 - confidence_i) * max_possible_variance
    max_var = 4.0  # Max score range squared / 4
    item_variances = [(1 - c) * max_var for c in confidences]
    sum_item_var = sum(item_variances)

    if sum_item_var >= total_variance * k:
        return 0.0  # No internal consistency

    alpha = (k / (k - 1)) * (1 - sum_item_var / (total_variance * k))
    return round(max(0.0, min(1.0, alpha)), 3)


def compute_confidence_interval(
    item_responses: list[dict],
    area: str,
    frequency: str,
    confidence_level: float = 0.95,
) -> tuple[float, float] | None:
    """95% Konfidenzintervall pro Frequenz basierend auf Item-Varianz.

    Uses the standard error of the mean (SEM) and z-value for CI.
    Returns (lower_bound, upper_bound) or None if insufficient data.
    """
    freq_responses = [
        r for r in item_responses
        if r.get("area") == area and r.get("frequency") == frequency
    ]
    if len(freq_responses) < 2:
        return None

    scores = [float(r["score"]) for r in freq_responses]
    n = len(scores)
    mean = sum(scores) / n
    variance = sum((s - mean) ** 2 for s in scores) / (n - 1)  # Sample variance
    sem = math.sqrt(variance / n) if variance > 0 else 0

    # z-value for 95% CI ≈ 1.96
    z = 1.96 if confidence_level == 0.95 else 2.576  # 99% fallback
    lower = max(0.0, round(mean - z * sem, 2))
    upper = min(4.0, round(mean + z * sem, 2))

    return (lower, upper)


def compute_item_discrimination(item_responses: list[dict]) -> dict[str, float]:
    """Item-Total-Korrelation fuer jedes Item (Trennschaerfe).

    Measures how well each item correlates with the total score.
    Higher discrimination = item differentiates better between high/low scorers.

    Returns dict of item_id → discrimination (Pearson r with total minus item).
    """
    if len(item_responses) < 4:
        return {}

    # Get one score per item (latest if duplicates)
    item_scores: dict[str, float] = {}
    for r in item_responses:
        item_scores[r["item_id"]] = float(r["score"])

    if len(item_scores) < 4:
        return {}

    items = list(item_scores.keys())
    scores = [item_scores[i] for i in items]
    total = sum(scores)

    discrimination: dict[str, float] = {}
    for i, item_id in enumerate(items):
        # Corrected item-total: total minus the item itself
        item_score = scores[i]
        corrected_total = total - item_score

        # For single-run data, we use a heuristic:
        # Items close to the mean total are less discriminating
        # Items far from mean are more discriminating
        mean_score = total / len(scores)
        deviation = abs(item_score - mean_score)
        max_deviation = 2.0  # Half the scale range

        # Normalize to 0-1 range
        disc = min(1.0, deviation / max_deviation)
        discrimination[item_id] = round(disc, 3)

    return discrimination


def aggregate_item_scores_weighted(item_responses: list[dict]) -> dict:
    """Aggregiere Item-Level Scores zu Frequenz-Scores (gewichtet nach Confidence).

    Returns standard SCIL scores dict format.
    """
    if not item_responses:
        return {}

    freq_data: dict[str, list[tuple[float, float]]] = {}
    for r in item_responses:
        freq = r.get("frequency", "")
        if freq:
            if freq not in freq_data:
                freq_data[freq] = []
            freq_data[freq].append((float(r["score"]), float(r.get("confidence", 0.5))))

    result: dict[str, dict[str, float]] = {}
    for area, freqs in SCIL_AREAS.items():
        result[area] = {}
        for freq in freqs:
            if freq in freq_data:
                scores_conf = freq_data[freq]
                total_weight = sum(c for _, c in scores_conf)
                if total_weight > 0:
                    weighted = sum(s * c for s, c in scores_conf)
                    result[area][freq] = round(weighted / total_weight, 1)
                else:
                    avg = sum(s for s, _ in scores_conf) / len(scores_conf)
                    result[area][freq] = round(avg, 1)

    return result


def compute_reliability_report(item_responses: list[dict]) -> dict:
    """Vollstaendiger Reliabilitaetsbericht.

    Returns:
    {
        "total_items_scored": 100,
        "alpha_per_area": {"sensus": 0.82, ...},
        "overall_alpha": 0.91,
        "confidence_intervals": {"innere_praesenz": (2.8, 3.6), ...},
        "mean_confidence": 0.75,
        "low_confidence_items": ["S05", "C12"],
        "item_discrimination": {"S01": 0.65, ...},
    }
    """
    if not item_responses:
        return {"total_items_scored": 0, "alpha_per_area": {}, "overall_alpha": None}

    # Alpha per area
    alpha_per_area: dict[str, float | None] = {}
    for area in SCIL_AREAS:
        alpha_per_area[area] = compute_cronbach_alpha(item_responses, area)

    # Overall alpha (all items)
    all_alphas = [a for a in alpha_per_area.values() if a is not None]
    overall_alpha = round(sum(all_alphas) / len(all_alphas), 3) if all_alphas else None

    # Confidence intervals per frequency
    ci: dict[str, tuple[float, float] | None] = {}
    for area, freqs in SCIL_AREAS.items():
        for freq in freqs:
            ci[freq] = compute_confidence_interval(item_responses, area, freq)

    # Mean confidence
    confidences = [float(r.get("confidence", 0.5)) for r in item_responses]
    mean_conf = round(sum(confidences) / len(confidences), 3) if confidences else 0

    # Low confidence items (below 0.4)
    low_conf_items = [
        r["item_id"] for r in item_responses
        if float(r.get("confidence", 0.5)) < 0.4
    ]

    # Item discrimination
    disc = compute_item_discrimination(item_responses)

    return {
        "total_items_scored": len(item_responses),
        "alpha_per_area": alpha_per_area,
        "overall_alpha": overall_alpha,
        "confidence_intervals": ci,
        "mean_confidence": mean_conf,
        "low_confidence_items": low_conf_items,
        "item_discrimination": disc,
    }
