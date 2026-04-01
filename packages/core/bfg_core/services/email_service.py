"""Email service — SES (production) / SMTP (development).

Provides async email delivery with template support:
- Production: AWS SES via aioboto3
- Development: SMTP to local MailHog/Mailpit via aiosmtplib

Usage:
    from bfg_core.services.email_service import EmailService

    svc = EmailService(settings)
    await svc.send("user@example.com", "Betreff", "<h1>HTML Body</h1>")
    await svc.send_template("user@example.com", "token_link", {"token_url": "..."})
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bfg_core.config import CoreSettings

logger = logging.getLogger(__name__)


# ===========================================================================
# Default Email Templates (German)
# ===========================================================================

_DEFAULT_TEMPLATES: dict[str, dict[str, str]] = {
    "token_link": {
        "subject": "Ihr Diagnostik-Token — {diagnostic_type}",
        "html": (
            "<h2>Ihr persoenlicher Diagnostik-Token</h2>"
            "<p>Sie haben einen Token fuer <strong>{diagnostic_type}</strong> ({tier}) erhalten.</p>"
            "<p>Aktivieren Sie Ihren Token hier:</p>"
            "<p><a href=\"{token_url}\" style=\"background:#E88D2A;color:white;padding:12px 24px;"
            "text-decoration:none;border-radius:6px;font-weight:bold;\">Token aktivieren</a></p>"
            "<p>Token-Code: <code>{token_code}</code></p>"
            "<p>Gueltig bis: {expires_at}</p>"
            "<hr><p style=\"color:#888;font-size:12px;\">Diese E-Mail wurde automatisch von der "
            "BFG-Plattform generiert.</p>"
        ),
    },
    "feedback_invitation": {
        "subject": "360-Feedback Einladung von {requester_name}",
        "html": (
            "<h2>Feedback-Einladung</h2>"
            "<p><strong>{requester_name}</strong> hat Sie eingeladen, Feedback zu geben.</p>"
            "<p>Ihre Angaben werden anonymisiert ausgewertet. Individuelle Antworten werden "
            "nicht an die Zielperson weitergegeben.</p>"
            "<p><a href=\"{feedback_url}\" style=\"background:#E88D2A;color:white;padding:12px 24px;"
            "text-decoration:none;border-radius:6px;font-weight:bold;\">Feedback geben</a></p>"
            "<p style=\"color:#888;font-size:12px;\">Rechtsgrundlage: Art. 6 Abs. 1 lit. a DSGVO. "
            "Sie koennen Ihre Einwilligung jederzeit widerrufen.</p>"
        ),
    },
    "result_ready": {
        "subject": "Ihre {diagnostic_type}-Ergebnisse sind bereit",
        "html": (
            "<h2>Ergebnisse verfuegbar</h2>"
            "<p>Ihre <strong>{diagnostic_type}</strong>-Diagnostik wurde ausgewertet.</p>"
            "<p><a href=\"{results_url}\" style=\"background:#E88D2A;color:white;padding:12px 24px;"
            "text-decoration:none;border-radius:6px;font-weight:bold;\">Ergebnisse ansehen</a></p>"
            "<hr><p style=\"color:#888;font-size:12px;\">Diese E-Mail wurde automatisch von der "
            "BFG-Plattform generiert.</p>"
        ),
    },
    "coach_invitation": {
        "subject": "Einladung zur SCIL-Diagnostik von {coach_name}",
        "html": (
            "<h2>Einladung zur SCIL-Wirkungsdiagnostik</h2>"
            "<p><strong>{coach_name}</strong> laedt Sie ein, an der SCIL-Wirkungsdiagnostik "
            "teilzunehmen.</p>"
            "<p>Die SCIL-Diagnostik analysiert Ihre Wirkung in vier Bereichen: "
            "Sensus, Corpus, Intellektus und Lingua. Sie erhalten ein persoenliches "
            "Wirkungsprofil mit konkreten Entwicklungsempfehlungen.</p>"
            "<p><a href=\"{invitation_url}\" style=\"background:#E88D2A;color:white;padding:12px 24px;"
            "text-decoration:none;border-radius:6px;font-weight:bold;\">Einladung annehmen</a></p>"
            "<p style=\"color:#888;font-size:13px;\">Die Diagnostik dauert ca. 30-45 Minuten. "
            "Ihre Antworten werden vertraulich behandelt.</p>"
            "<hr><p style=\"color:#888;font-size:12px;\">Diese E-Mail wurde automatisch von der "
            "BFG-Plattform im Auftrag von {coach_name} generiert.</p>"
        ),
    },
}


class EmailService:
    """Async email delivery with environment-aware transport."""

    def __init__(self, settings: CoreSettings):
        self._settings = settings
        self._templates: dict[str, dict[str, str]] = dict(_DEFAULT_TEMPLATES)

    def register_template(self, name: str, subject: str, html: str) -> None:
        """Register or override an email template.

        Templates use Python format strings: {variable_name}
        """
        self._templates[name] = {"subject": subject, "html": html}

    async def send(
        self,
        to: str,
        subject: str,
        html_body: str,
        *,
        text_body: str | None = None,
    ) -> bool:
        """Send an email. Returns True on success, False on failure.

        Transport selection:
        - environment == "production": AWS SES
        - otherwise: SMTP (MailHog/Mailpit)
        """
        if self._settings.environment == "production":
            return await self._send_ses(to, subject, html_body, text_body)
        else:
            return await self._send_smtp(to, subject, html_body, text_body)

    async def send_template(
        self,
        to: str,
        template_name: str,
        context: dict,
    ) -> bool:
        """Send a templated email. Context dict is used for string formatting."""
        tmpl = self._templates.get(template_name)
        if not tmpl:
            logger.error("Email template not found: %s", template_name)
            return False

        try:
            subject = tmpl["subject"].format(**context)
            html_body = tmpl["html"].format(**context)
        except KeyError as e:
            logger.error("Missing template variable %s for template %s", e, template_name)
            return False

        return await self.send(to, subject, html_body)

    # ------------------------------------------------------------------
    # Transport: SMTP (development)
    # ------------------------------------------------------------------

    async def _send_smtp(
        self, to: str, subject: str, html_body: str, text_body: str | None,
    ) -> bool:
        try:
            import aiosmtplib

            msg = MIMEMultipart("alternative")
            msg["From"] = self._settings.email_from
            msg["To"] = to
            msg["Subject"] = subject

            if text_body:
                msg.attach(MIMEText(text_body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            await aiosmtplib.send(
                msg,
                hostname=self._settings.smtp_host,
                port=self._settings.smtp_port,
                use_tls=False,
            )
            logger.info("Email sent via SMTP to %s: %s", to, subject)
            return True

        except ImportError:
            logger.warning(
                "aiosmtplib not installed. Install with: pip install aiosmtplib. "
                "Email to %s NOT sent.", to,
            )
            return False
        except Exception as e:
            logger.error("SMTP send failed to %s: %s", to, e, exc_info=True)
            return False

    # ------------------------------------------------------------------
    # Transport: AWS SES (production)
    # ------------------------------------------------------------------

    async def _send_ses(
        self, to: str, subject: str, html_body: str, text_body: str | None,
    ) -> bool:
        try:
            import aioboto3

            session = aioboto3.Session()
            async with session.client(
                "ses",
                region_name=self._settings.ses_region,
            ) as ses:
                body: dict = {"Html": {"Data": html_body, "Charset": "UTF-8"}}
                if text_body:
                    body["Text"] = {"Data": text_body, "Charset": "UTF-8"}

                await ses.send_email(
                    Source=self._settings.email_from,
                    Destination={"ToAddresses": [to]},
                    Message={
                        "Subject": {"Data": subject, "Charset": "UTF-8"},
                        "Body": body,
                    },
                )

            logger.info("Email sent via SES to %s: %s", to, subject)
            return True

        except ImportError:
            logger.warning(
                "aioboto3 not installed. Install with: pip install aioboto3. "
                "Email to %s NOT sent.", to,
            )
            return False
        except Exception as e:
            logger.error("SES send failed to %s: %s", to, e, exc_info=True)
            return False
