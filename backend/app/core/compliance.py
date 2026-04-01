"""
Compliance Layer — EU AI Act & DSGVO Checks

This module provides:
  1. EU AI Act risk classification for diagnostics
  2. DSGVO consent management utilities
  3. Data retention enforcement
  4. De-identification of qualitative feedback
  5. Audit logging for compliance documentation
"""

import re
import uuid
from enum import Enum
from datetime import datetime, timedelta
from dataclasses import dataclass, field


# ── EU AI Act Risk Classification ────────────────────────────

class AIActRiskLevel(str, Enum):
    PROHIBITED = "prohibited"          # Art. 5 — forbidden uses
    HIGH_RISK = "high_risk"            # Annex III — requires full compliance
    LIMITED_RISK = "limited_risk"      # Transparency obligations only
    MINIMAL_RISK = "minimal_risk"      # No specific obligations


class UsageContext(str, Enum):
    B2C_SELF_COACHING = "b2c_self_coaching"
    HR_RECRUITING = "hr_recruiting"
    HR_PERFORMANCE = "hr_performance"
    EDUCATION = "education"
    WORKPLACE_MONITORING = "workplace_monitoring"
    BIOMETRIC_EMOTION = "biometric_emotion"


@dataclass
class ComplianceCheck:
    """Result of a compliance check."""
    is_compliant: bool
    risk_level: AIActRiskLevel
    context: UsageContext
    requirements: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


def classify_ai_act_risk(context: UsageContext) -> ComplianceCheck:
    """
    Classify the AI Act risk level based on usage context.

    EU AI Act key dates:
      - 2 Feb 2025: Prohibited practices banned
      - 2 Aug 2025: Rules for general-purpose AI
      - 2 Aug 2026: Full High-Risk system rules

    Gr8hub classification:
      - B2C self-coaching: NOT high-risk (no employment context)
      - HR/Recruiting: HIGH-RISK (Annex III, area 4: Employment)
      - Biometric emotion at workplace: PROHIBITED (Art. 5)
    """

    if context == UsageContext.BIOMETRIC_EMOTION:
        return ComplianceCheck(
            is_compliant=False,
            risk_level=AIActRiskLevel.PROHIBITED,
            context=context,
            blockers=[
                "Art. 5 EU AI Act: Emotion recognition based on biometric data "
                "in the workplace is PROHIBITED.",
                "This applies from 2 February 2025.",
                "Only text-based emotion/sentiment analysis is permitted.",
            ],
        )

    if context in (UsageContext.HR_RECRUITING, UsageContext.HR_PERFORMANCE):
        return ComplianceCheck(
            is_compliant=True,  # Compliant IF requirements are met
            risk_level=AIActRiskLevel.HIGH_RISK,
            context=context,
            requirements=[
                "Art. 9: Risk management system required",
                "Art. 10: Data quality and data governance required",
                "Art. 11: Technical documentation required",
                "Art. 13: Transparency and information obligations",
                "Art. 14: Human oversight mandatory",
                "Art. 15: Accuracy, robustness, and cybersecurity",
                "EU Conformity declaration + CE marking required",
                "DIN 33430 compliance recommended for DACH region",
                "§87 BetrVG: Works council co-determination required (DACH)",
            ],
            warnings=[
                "Full compliance required by 2 August 2026.",
                "Profiling natural persons is automatically high-risk.",
                "Consider Art. 28 DSGVO (AVV) for external processing.",
            ],
        )

    if context == UsageContext.WORKPLACE_MONITORING:
        return ComplianceCheck(
            is_compliant=True,
            risk_level=AIActRiskLevel.HIGH_RISK,
            context=context,
            requirements=[
                "Same High-Risk requirements as HR context",
                "Additional: Employee notification mandatory",
                "Works council agreement required (§87 BetrVG)",
            ],
            warnings=[
                "Consider whether this crosses into PROHIBITED territory "
                "if biometric data is involved."
            ],
        )

    if context == UsageContext.EDUCATION:
        return ComplianceCheck(
            is_compliant=True,
            risk_level=AIActRiskLevel.HIGH_RISK,
            context=context,
            requirements=[
                "Annex III, area 3: Education context is high-risk",
                "Transparency obligations apply",
            ],
        )

    # B2C self-coaching — not high-risk
    return ComplianceCheck(
        is_compliant=True,
        risk_level=AIActRiskLevel.MINIMAL_RISK,
        context=context,
        requirements=[
            "General transparency: Inform users they interact with AI",
            "Art. 52: Disclosure that content is AI-generated",
        ],
        warnings=[
            "If the platform is used in an employment context by the user's "
            "employer, the risk level escalates to HIGH_RISK.",
        ],
    )


# ── DSGVO Consent Management ────────────────────────────────

@dataclass
class ConsentRecord:
    """Tracks a user's GDPR consent."""
    user_id: str
    consent_type: str          # "diagnostic", "360_feedback_rater", "360_feedback_target", "import"
    consent_text: str
    consented: bool
    consented_at: datetime | None = None
    withdrawn_at: datetime | None = None
    ip_address: str | None = None  # Optional, for legal documentation


CONSENT_TEXTS = {
    "diagnostic": (
        "Ich willige ein, dass meine Antworten und Diagnostik-Ergebnisse verarbeitet werden. "
        "Die Daten werden ausschließlich zur Erstellung meines persönlichen Profils genutzt. "
        "Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO. "
        "Bei besonderen Kategorien: Art. 9 Abs. 2 lit. a DSGVO."
    ),
    "360_feedback_rater": (
        "Ich willige ein, dass mein Feedback anonymisiert verarbeitet wird. "
        "Individuelle Antworten werden nie an die Zielperson weitergegeben. "
        "Die Daten werden nach {retention_months} Monaten automatisch gelöscht."
    ),
    "360_feedback_target": (
        "Ich willige ein, dass 360°-Feedback über mich gesammelt und aggregiert wird. "
        "Ich erhalte nur zusammengefasste Ergebnisse, nie einzelne Rater-Antworten. "
        "Gruppen mit weniger als {min_raters} Ratern werden nicht ausgewertet."
    ),
    "import": (
        "Ich bestätige, dass ich berechtigt bin, diese Testergebnisse hochzuladen, "
        "und willige in deren Verarbeitung auf der Gr8hub-Plattform ein. "
        "Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO."
    ),
}


def get_consent_text(consent_type: str, **kwargs) -> str:
    """Get the localized consent text for a specific purpose."""
    text = CONSENT_TEXTS.get(consent_type, "")
    return text.format(**kwargs) if kwargs else text


# ── De-Identification of Qualitative Feedback ────────────────

# Patterns to detect and remove personally identifiable information
PII_PATTERNS = [
    # Email addresses
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[E-MAIL ENTFERNT]"),
    # Phone numbers (German/international)
    (r"\b(\+\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b", "[TELEFON ENTFERNT]"),
    # German date patterns
    (r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b", "[DATUM ENTFERNT]"),
    # Specific role/department mentions that could identify
    (r"\b(Abteilungsleiter|Teamleiter|CEO|CTO|CFO|COO|VP|Director)\s+\w+\b", "[ROLLE ENTFERNT]"),
]


def deidentify_text(text: str, target_name: str = "") -> tuple[str, list[str]]:
    """
    Remove personally identifiable information from qualitative feedback text.

    Returns:
        tuple: (cleaned_text, list of removals made)
    """
    removals = []

    # Remove target name references (replace with [PERSON])
    if target_name:
        parts = target_name.split()
        for part in parts:
            if len(part) > 2:  # Skip short words like "Dr."
                count = text.lower().count(part.lower())
                if count > 0:
                    text = re.sub(re.escape(part), "[PERSON]", text, flags=re.IGNORECASE)
                    removals.append(f"Name '{part}' removed ({count}x)")

    # Apply PII patterns
    for pattern, replacement in PII_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            text = re.sub(pattern, replacement, text)
            removals.append(f"Pattern matched: {len(matches)}x → {replacement}")

    return text, removals


# ── Data Retention ───────────────────────────────────────────

def compute_deletion_date(
    created_at: datetime,
    retention_months: int = 24,
) -> datetime:
    """Compute the scheduled deletion date based on retention policy."""
    return created_at + timedelta(days=retention_months * 30)


def is_past_retention(created_at: datetime, retention_months: int = 24) -> bool:
    """Check if data has exceeded its retention period."""
    deletion_date = compute_deletion_date(created_at, retention_months)
    return datetime.utcnow() > deletion_date


# ── Audit Logging ────────────────────────────────────────────

@dataclass
class AuditEntry:
    """Structured audit log entry for compliance documentation."""
    event_type: str           # "consent_given", "data_accessed", "data_deleted", etc.
    user_id: str
    resource_type: str        # "diagnostic_run", "feedback_round", "imported_result"
    resource_id: str
    details: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "user_id": self.user_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class ComplianceAuditLog:
    """In-memory audit log (in production: persist to DB or external service)."""

    def __init__(self):
        self._entries: list[AuditEntry] = []

    def log(self, entry: AuditEntry):
        self._entries.append(entry)

    def log_consent(self, user_id: str, consent_type: str, resource_id: str):
        self.log(AuditEntry(
            event_type="consent_given",
            user_id=user_id,
            resource_type=consent_type,
            resource_id=resource_id,
            details={"consent_type": consent_type},
        ))

    def log_data_access(self, user_id: str, resource_type: str, resource_id: str):
        self.log(AuditEntry(
            event_type="data_accessed",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
        ))

    def log_data_deletion(self, user_id: str, resource_type: str, resource_id: str, reason: str = ""):
        self.log(AuditEntry(
            event_type="data_deleted",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"reason": reason},
        ))

    def get_entries(self, user_id: str | None = None) -> list[dict]:
        entries = self._entries
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]
        return [e.to_dict() for e in entries]


# Global audit log instance
audit_log = ComplianceAuditLog()


# ── IP Rights Validation ─────────────────────────────────────

PROPRIETARY_TOOLS = {
    "mbti", "disc", "disg", "persolog", "insights", "reiss", "lumina",
    "9levels", "captain", "hogan", "cliftonstrengths", "pcm", "hbdi",
    "biostruktur", "structogram", "profilingvalues",
}

OWN_DIAGNOSTICS = {
    "scil", "big_five", "values_schwartz", "eq_trait", "resilience",
    "stress_coping", "team_roles", "communication_style", "motivation_sdt",
    "thinking_styles", "cognitive_flexibility", "feedback_360",
}


def validate_ip_rights(diagnostic_slug: str, action: str) -> dict:
    """
    Validate that an action respects IP rights.

    Actions: "conduct" (run diagnostic), "import" (import scores), "display" (show results)
    """
    if diagnostic_slug in OWN_DIAGNOSTICS:
        return {
            "allowed": True,
            "diagnostic": diagnostic_slug,
            "action": action,
            "ip_status": "own_implementation",
            "notes": "Eigene Implementierung — vollständiger Zugriff erlaubt.",
        }

    if diagnostic_slug in PROPRIETARY_TOOLS:
        if action == "conduct":
            return {
                "allowed": False,
                "diagnostic": diagnostic_slug,
                "action": action,
                "ip_status": "proprietary",
                "notes": (
                    f"'{diagnostic_slug}' ist markenrechtlich geschützt. "
                    "Durchführung eigener Items für dieses Konstrukt ist NICHT erlaubt. "
                    "Nur Import bestehender Ergebnisse ist zulässig."
                ),
            }
        elif action in ("import", "display"):
            return {
                "allowed": True,
                "diagnostic": diagnostic_slug,
                "action": action,
                "ip_status": "proprietary_import_only",
                "notes": (
                    "Import und Anzeige reiner Score-Werte ist mit Nutzer-Einwilligung erlaubt. "
                    "KEINE Übernahme von Items, Report-Texten oder grafischen Gestaltungen."
                ),
            }

    return {
        "allowed": False,
        "diagnostic": diagnostic_slug,
        "action": action,
        "ip_status": "unknown",
        "notes": "Unbekanntes Diagnostik-Tool. Bitte IP-Status prüfen.",
    }
