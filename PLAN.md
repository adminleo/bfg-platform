# SCIL 100-Fragen Refactoring — Wissenschaftlich fundierte Erhebung

## Kernproblem
Aktuell: Agent stellt frei ~15-20 Fragen, AI rät Scores → **nicht statistisch belastbar**
Ziel: **100 strukturierte Items (25 pro Cluster)**, konversationell verpackt, per-Item Scoring, Psychometrie-ready

## Architektur-Entscheidungen

### A. Item Pool: JSON-Konfigurationsdatei (`scil_items.py`)
- 100 Items als Python-Datenstruktur (leicht versionierbar, kein DB-Overhead)
- Jedes Item: `id`, `area`, `frequency`, `text_de`, `scoring_guidance`, `reverse_scored`
- 25 Items pro Cluster, ~6 pro Frequenz (manche Frequenzen teilen Items)
- Später: Migration zu DB-Tabelle für dynamisches Item-Management

### B. Agent-Architektur: Hybrid — Strukturierter Plan, konversationelle Umsetzung
- Agent bekommt den **nächsten Item-Block** (3-4 Items aus aktuellem Cluster)
- AI formuliert die Items als natürliches Gespräch (nicht Fragebogen-Style)
- Nach jeder Antwort: AI scored gezielt die adressierten Frequenzen via tool_use
- Cluster-Rotation: S→C→I→L→S→C→I→L... (je 6-7 Items pro Runde, 4 Runden)

### C. Per-Item Scoring + Psychometrie
- Jede Antwort → `score_item` tool_use mit Item-ID + Score(s) + Confidence
- `item_responses` JSONB auf DiagnosticRun für vollständige Item-Level-Daten
- Cronbach's Alpha pro Cluster, Konfidenzintervalle, Item-Diskrimination
- `percentiles` und `norm_group` auf DiagnosticResult endlich befüllen

### D. ML Future-Proofing
- Item-Response-Daten (item_id, score, response_time_ms, confidence) → IRT-ready
- Item-Parameter-Felder (difficulty, discrimination) im Item-Pool vorbereitet
- Architektur erlaubt später adaptive Verkürzung auf Basis kalibrierter Items

---

## Implementierungsplan (8 Schritte)

### Schritt 1: Item-Pool erstellen
**Neue Datei:** `apps/scil/backend/app/services/scil_items.py` (~800 Zeilen)

```
SCIL_ITEM_POOL = [
    {
        "id": "S01",
        "area": "sensus",
        "frequency": "innere_praesenz",
        "text_de": "Wenn Sie sich in einem Gespräch befinden — wie präsent sind Sie im Moment? Beschreiben Sie eine typische Situation.",
        "scoring_guidance": "Hohe Präsenz = aktives Zuhören, Blickkontakt-Beschreibung, Hier-und-Jetzt. Niedrig = Abschweifen, Multitasking.",
        "reverse_scored": false,
        "difficulty": 0.5,       # IRT-Parameter (initial neutral)
        "discrimination": 1.0,   # IRT-Parameter (initial neutral)
    },
    ... # 100 Items total
]
```

Verteilung: 25 Sensus (S01-S25), 25 Corpus (C01-C25), 25 Intellektus (I01-I25), 25 Lingua (L01-L25)
Pro Frequenz: ~6 Items (25 Items / 4 Frequenzen = 6.25)

Hilfsfunktionen:
- `get_items_for_area(area) -> list`
- `get_items_for_frequency(area, freq) -> list`
- `get_next_item_block(answered_ids, current_area) -> list[Item]`
- `get_cluster_progress(answered_ids) -> dict[str, int]` (z.B. {"sensus": 18, "corpus": 12, ...})

### Schritt 2: `score_item` Tool für granulares Per-Item Scoring
**Änderung:** `diagnosis_agent.py` — neues Tool neben `update_scil_scores`

```python
SCORE_ITEM_TOOL = {
    "name": "score_item",
    "description": "Bewerte die Antwort des Nutzers für ein spezifisches SCIL-Item.",
    "input_schema": {
        "type": "object",
        "properties": {
            "item_id": {"type": "string", "description": "Item-ID (z.B. S01, C12, I03)"},
            "score": {"type": "number", "minimum": 0, "maximum": 4},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1,
                          "description": "Wie sicher bist du bei dieser Bewertung? 0=unsicher, 1=sehr sicher"},
            "reasoning": {"type": "string", "description": "Kurze Begründung (intern)"},
        },
        "required": ["item_id", "score", "confidence"],
    },
}
```

Der Agent kann mehrere `score_item` Calls pro Turn machen (eine Antwort kann mehrere Items adressieren).

### Schritt 3: Agent-Refactoring — Item-gesteuerter Assessment-Loop
**Änderung:** `diagnosis_agent.py` — Kernlogik komplett neu

State Machine wird:
```
GREETING → CLUSTER_SENSUS → CLUSTER_CORPUS → CLUSTER_INTELLEKTUS → CLUSTER_LINGUA → SCORING → SUMMARY → COMPLETED
```

Ablauf pro Cluster (~25 Items, ~8-10 Turns):
1. Agent bekommt nächsten Item-Block (3-4 Items)
2. System-Prompt enthält: Item-Texte, Scoring-Guidance, bisherige Scores
3. Agent formuliert konversationelle Frage die 3-4 Items abdeckt
4. User antwortet
5. Agent ruft `score_item` für jedes adressierte Item auf
6. Repeat bis 25 Items im Cluster scored

Schlüsseländerungen:
- `progress = total_scored_items / 100` (statt question_count/20)
- `should_complete` wenn alle 100 Items scored (oder ≥96 mit hoher Confidence)
- Cluster-Übergang nach 25 Items pro Bereich
- Context Budgeting: Nur letzte ~10 Messages + Cluster-Summary im Prompt

### Schritt 4: DiagnosticRun erweitern — `item_responses` JSONB
**Änderung:** `packages/core/bfg_core/models/diagnostic.py`

```python
class DiagnosticRun(Base):
    ...
    item_responses: Mapped[list] = mapped_column(JSONB, default=list)
    # Format: [{"item_id": "S01", "score": 3.2, "confidence": 0.8,
    #           "reasoning": "...", "scored_at": "...", "turn_number": 5}]
```

`answers` bleibt für aggregierte Scores (Kompatibilität mit Polygon-UI).
`item_responses` speichert die granularen Per-Item-Daten.

### Schritt 5: Psychometrie-Engine erweitern
**Änderung:** `apps/scil/backend/app/services/scil_scoring.py` — Neue Funktionen

```python
def compute_cronbach_alpha(item_responses: list, area: str) -> float:
    """Cronbach's Alpha für internen Konsistenzcheck pro Cluster."""

def compute_confidence_interval(scores: dict, item_responses: list, area: str) -> tuple[float, float]:
    """95% Konfidenzintervall pro Frequenz basierend auf Item-Varianz."""

def compute_item_discrimination(item_responses: list) -> dict[str, float]:
    """Item-Total-Korrelation für jedes Item (Trennschärfe)."""

def aggregate_item_scores(item_responses: list) -> dict:
    """Aggregiere Item-Level Scores zu Frequenz-Scores (gewichtet nach Confidence)."""

def compute_reliability_report(item_responses: list) -> dict:
    """Vollständiger Reliabilitätsbericht: Alpha, SEM, Split-Half."""
```

Aggregation: Frequenz-Score = gewichteter Mittelwert aller Items dieser Frequenz, gewichtet nach AI-Confidence.

### Schritt 6: Seed-Daten und Konfiguration aktualisieren
**Änderung:** `scil_seed.py`

- `min_questions` → 100
- `max_questions` → 120 (Puffer für Nachfragen)
- Config um Item-Pool-Version erweitern

### Schritt 7: SSE Events und Routes erweitern
**Änderung:** `scil_routes.py` + `useSSEChat.ts`

Neues SSE Event:
```json
{
    "type": "cluster_progress",
    "cluster": {"sensus": 25, "corpus": 12, "intellektus": 0, "lingua": 0},
    "total_scored": 37,
    "total_required": 100
}
```

Session-Detail-Endpoint: `item_responses` Count und Cluster-Progress mitliefern.

### Schritt 8: Frontend — Cluster-Progress-Anzeige
**Änderung:** `ScoreProgress.tsx` + `RightSidebar.tsx`

ScoreProgress: 4 Fortschrittsbalken (S, C, I, L) statt einem Gesamtbalken.
Jeder zeigt X/25 Items.
Gesamtfortschritt: X/100.

---

## Offene Frage an dich (Leonardo)

Bevor ich die 100 Items schreibe, brauche ich deinen Input:

**Die Items selbst:** Hast du einen bestehenden SCIL-Fragebogen / Item-Katalog den wir als Basis nehmen? Die 100 Items müssen fachlich korrekt sein — ich kann Entwürfe generieren, aber die finale Validierung muss durch SCIL-Expertise passieren.

Möglichkeiten:
1. Du lieferst den Original-SCIL-Item-Katalog → ich implementiere 1:1
2. Ich generiere 100 Entwurfs-Items basierend auf der SCIL-Theorie → du reviewst
3. Wir starten mit Cluster-Struktur + Platzhalter-Items → du ersetzt sie später

---

## ML-Perspektive (Zukunft)

Mit den Per-Item-Response-Daten (`item_responses`) können wir nach Datensammlung:

1. **Item Response Theory (IRT)**: 2PL/3PL-Modelle kalibrieren → welche Items sind diskriminativ?
2. **Computerized Adaptive Testing (CAT)**: Item-Auswahl basierend auf bisherigen Antworten → statt 100 vielleicht 40-60 Items bei gleicher Genauigkeit
3. **Item-Cluster-Analyse**: Welche Items sind redundant? Faktorenanalyse zur Validierung der 4-Cluster-Struktur
4. **Confidence-Kalibrierung**: AI-Confidence vs. tatsächliche Reliabilität vergleichen

Dafür brauchen wir ~200+ vollständige Durchläufe. Die Architektur speichert ab Tag 1 die richtigen Daten.
