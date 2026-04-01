"""Consent Service — Immutable DSGVO consent audit trail.

Consent is tracked as an append-only audit trail using ComplianceAuditLog.
The effective consent per type is determined by the most recent row.

Pattern ported from cNode consent_service.py, adapted to use BFG's
existing ComplianceAuditLog model and async sessions.

Usage:
    from bfg_core.services.consent_service import ConsentService

    svc = ConsentService(session_factory)
    await svc.record_consent("user-123", "diagnostic", ip_address="192.168.1.1")
    status = await svc.get_consent_status("user-123", "diagnostic")
    # {"consented": True, "consented_at": ..., "consent_type": "diagnostic", ...}
"""

import logging
from datetime import datetime

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import async_sessionmaker

from bfg_core.compliance.dsgvo import CONSENT_TEXTS, get_consent_text
from bfg_core.models.audit import ComplianceAuditLog

logger = logging.getLogger(__name__)

# Consent version — bump when consent text changes to trigger reconsent
CONSENT_VERSION = "1.0"

# All recognized consent types
CONSENT_TYPES = {
    "diagnostic",
    "360_feedback_rater",
    "360_feedback_target",
    "import",
    "marketing",
}


class ConsentService:
    """Immutable consent recording and querying via ComplianceAuditLog."""

    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def record_consent(
        self,
        user_id: str,
        consent_type: str,
        *,
        resource_type: str = "platform",
        resource_id: str = "global",
        ip_address: str | None = None,
        consent_text_override: str | None = None,
    ) -> ComplianceAuditLog:
        """Record a consent-given event. Always INSERT, never UPDATE.

        Args:
            user_id: User identifier (UUID as string).
            consent_type: One of CONSENT_TYPES (e.g., "diagnostic", "marketing").
            resource_type: What the consent is for (default: "platform").
            resource_id: Specific resource ID (default: "global").
            ip_address: Client IP for audit purposes.
            consent_text_override: Override the default consent text.

        Returns:
            The created ComplianceAuditLog entry.
        """
        consent_text = consent_text_override or get_consent_text(consent_type)

        async with self._session_factory() as session:
            entry = ComplianceAuditLog(
                event_type="consent_given",
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                details={
                    "consent_type": consent_type,
                    "consent_text": consent_text,
                    "ip_address": ip_address,
                    "version": CONSENT_VERSION,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)

        logger.info(
            "Consent recorded: user=%s type=%s resource=%s/%s",
            user_id, consent_type, resource_type, resource_id,
        )
        return entry

    async def withdraw_consent(
        self,
        user_id: str,
        consent_type: str,
        *,
        reason: str | None = None,
        resource_type: str = "platform",
        resource_id: str = "global",
    ) -> ComplianceAuditLog:
        """Record a consent-withdrawn event. Append-only — never modifies existing rows.

        Returns:
            The created ComplianceAuditLog entry.
        """
        async with self._session_factory() as session:
            entry = ComplianceAuditLog(
                event_type="consent_withdrawn",
                user_id=user_id,
                resource_type=resource_type,
                resource_id=resource_id,
                details={
                    "consent_type": consent_type,
                    "withdrawal_reason": reason,
                    "version": CONSENT_VERSION,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            session.add(entry)
            await session.commit()
            await session.refresh(entry)

        logger.info("Consent withdrawn: user=%s type=%s", user_id, consent_type)
        return entry

    async def get_consent_status(self, user_id: str, consent_type: str) -> dict:
        """Get the current effective consent status for a user + consent type.

        Looks at the most recent consent event for this user + type combination.

        Returns:
            {
                "consented": bool,
                "consent_type": str,
                "consented_at": datetime | None,
                "withdrawn_at": datetime | None,
                "consent_text": str,
                "version": str,
            }
        """
        async with self._session_factory() as session:
            # Find the most recent consent event for this user + type
            stmt = (
                select(ComplianceAuditLog)
                .where(
                    and_(
                        ComplianceAuditLog.user_id == user_id,
                        ComplianceAuditLog.event_type.in_(["consent_given", "consent_withdrawn"]),
                    )
                )
                .order_by(desc(ComplianceAuditLog.created_at))
            )
            result = await session.execute(stmt)
            rows = list(result.scalars().all())

        # Filter by consent_type in details JSONB
        for row in rows:
            details = row.details or {}
            if details.get("consent_type") == consent_type:
                is_given = row.event_type == "consent_given"
                return {
                    "consented": is_given,
                    "consent_type": consent_type,
                    "consented_at": row.created_at if is_given else None,
                    "withdrawn_at": row.created_at if not is_given else None,
                    "consent_text": details.get("consent_text", ""),
                    "version": details.get("version", ""),
                }

        # No consent record found
        return {
            "consented": False,
            "consent_type": consent_type,
            "consented_at": None,
            "withdrawn_at": None,
            "consent_text": "",
            "version": "",
        }

    async def check_needs_reconsent(
        self,
        user_id: str,
        consent_type: str,
        current_version: str = CONSENT_VERSION,
    ) -> bool:
        """Check if the user needs to reconsent due to updated consent text.

        Returns True if:
        - User has never consented, or
        - User's consent was for an older version, or
        - User has withdrawn consent
        """
        status = await self.get_consent_status(user_id, consent_type)

        if not status["consented"]:
            return True

        if status["version"] != current_version:
            return True

        return False

    async def get_user_consents(self, user_id: str) -> list[dict]:
        """Get consent status for all consent types for a user.

        Returns a list of consent status dicts (one per consent type).
        """
        results = []
        for consent_type in sorted(CONSENT_TYPES):
            status = await self.get_consent_status(user_id, consent_type)
            results.append(status)
        return results
