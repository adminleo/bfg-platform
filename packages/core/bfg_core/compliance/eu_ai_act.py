"""EU AI Act risk classification for diagnostic platforms."""

from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field


class AIActRiskLevel(str, Enum):
    PROHIBITED = "prohibited"
    HIGH_RISK = "high_risk"
    LIMITED_RISK = "limited_risk"
    MINIMAL_RISK = "minimal_risk"


class UsageContext(str, Enum):
    B2C_SELF_COACHING = "b2c_self_coaching"
    HR_RECRUITING = "hr_recruiting"
    HR_PERFORMANCE = "hr_performance"
    EDUCATION = "education"
    WORKPLACE_MONITORING = "workplace_monitoring"
    BIOMETRIC_EMOTION = "biometric_emotion"


@dataclass
class ComplianceCheck:
    is_compliant: bool
    risk_level: AIActRiskLevel
    context: UsageContext
    requirements: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


def classify_ai_act_risk(context: UsageContext) -> ComplianceCheck:
    if context == UsageContext.BIOMETRIC_EMOTION:
        return ComplianceCheck(
            is_compliant=False,
            risk_level=AIActRiskLevel.PROHIBITED,
            context=context,
            blockers=[
                "Art. 5 EU AI Act: Emotion recognition based on biometric data "
                "in the workplace is PROHIBITED.",
            ],
        )

    if context in (UsageContext.HR_RECRUITING, UsageContext.HR_PERFORMANCE):
        return ComplianceCheck(
            is_compliant=True,
            risk_level=AIActRiskLevel.HIGH_RISK,
            context=context,
            requirements=[
                "Art. 9: Risk management system required",
                "Art. 10: Data quality and data governance required",
                "Art. 13: Transparency and information obligations",
                "Art. 14: Human oversight mandatory",
                "Art. 15: Accuracy, robustness, and cybersecurity",
                "DIN 33430 compliance recommended for DACH region",
            ],
            warnings=[
                "Full compliance required by 2 August 2026.",
                "Profiling natural persons is automatically high-risk.",
            ],
        )

    if context == UsageContext.WORKPLACE_MONITORING:
        return ComplianceCheck(
            is_compliant=True,
            risk_level=AIActRiskLevel.HIGH_RISK,
            context=context,
            requirements=[
                "Same High-Risk requirements as HR context",
                "Employee notification mandatory",
                "Works council agreement required",
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

    return ComplianceCheck(
        is_compliant=True,
        risk_level=AIActRiskLevel.MINIMAL_RISK,
        context=context,
        requirements=[
            "General transparency: Inform users they interact with AI",
            "Art. 52: Disclosure that content is AI-generated",
        ],
    )
