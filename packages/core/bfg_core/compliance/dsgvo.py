"""DSGVO consent management and data retention utilities."""

from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class ConsentRecord:
    user_id: str
    consent_type: str
    consent_text: str
    consented: bool
    consented_at: datetime | None = None
    withdrawn_at: datetime | None = None
    ip_address: str | None = None


CONSENT_TEXTS = {
    "diagnostic": (
        "Ich willige ein, dass meine Antworten und Diagnostik-Ergebnisse verarbeitet werden. "
        "Die Daten werden ausschliesslich zur Erstellung meines persoenlichen Profils genutzt. "
        "Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO."
    ),
    "360_feedback_rater": (
        "Ich willige ein, dass mein Feedback anonymisiert verarbeitet wird. "
        "Individuelle Antworten werden nie an die Zielperson weitergegeben. "
        "Die Daten werden nach {retention_months} Monaten automatisch geloescht."
    ),
    "360_feedback_target": (
        "Ich willige ein, dass 360-Feedback ueber mich gesammelt und aggregiert wird. "
        "Ich erhalte nur zusammengefasste Ergebnisse, nie einzelne Rater-Antworten. "
        "Gruppen mit weniger als {min_raters} Ratern werden nicht ausgewertet."
    ),
    "import": (
        "Ich bestaetige, dass ich berechtigt bin, diese Testergebnisse hochzuladen, "
        "und willige in deren Verarbeitung auf der Plattform ein. "
        "Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO."
    ),
    "marketing": (
        "Ich willige ein, dass ich per E-Mail ueber Neuigkeiten und Angebote "
        "der BFG-Plattform informiert werde. Ich kann diese Einwilligung jederzeit widerrufen. "
        "Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO."
    ),
}


def get_consent_text(consent_type: str, **kwargs) -> str:
    text = CONSENT_TEXTS.get(consent_type, "")
    return text.format(**kwargs) if kwargs else text


def compute_deletion_date(created_at: datetime, retention_months: int = 24) -> datetime:
    return created_at + timedelta(days=retention_months * 30)


def is_past_retention(created_at: datetime, retention_months: int = 24) -> bool:
    return datetime.utcnow() > compute_deletion_date(created_at, retention_months)
