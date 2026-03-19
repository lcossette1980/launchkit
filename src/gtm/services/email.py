"""Email service for magic link authentication.

When smtp_host is empty (default in dev), magic links are printed
to stdout/logs. In production, sends via SMTP with PII redacted in logs.
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from gtm.config import Settings

logger = logging.getLogger(__name__)


def send_magic_link(settings: Settings, email: str, token: str) -> None:
    """Send a magic link to the given email address."""
    link = f"{settings.app_url}/api/v1/auth/verify?token={token}"

    if not settings.smtp_host:
        # Dev mode: print directly to stdout so it's visible in docker logs
        # (logger.info can get buried in DEBUG noise)
        print(
            "\n"
            "╔══════════════════════════════════════════════════════════╗\n"
            f"║  MAGIC LINK for {email}\n"
            f"║  {link}\n"
            "╚══════════════════════════════════════════════════════════╝\n",
            flush=True,
        )
        return

    # Production: send real email via SMTP
    subject = "Sign in to VCLaunchKit"
    html_body = f"""
    <div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px">
        <h2 style="color:#6366f1">VCLaunchKit</h2>
        <p>Click the button below to sign in:</p>
        <a href="{link}"
           style="display:inline-block;padding:12px 24px;background:#6366f1;
                  color:#fff;border-radius:8px;text-decoration:none;
                  font-weight:600;margin:16px 0">
            Sign In
        </a>
        <p style="color:#888;font-size:13px;margin-top:24px">
            This link expires in {settings.magic_link_expiry_minutes} minutes.
            If you didn't request this, you can safely ignore it.
        </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = email
    msg.attach(MIMEText(f"Sign in to LaunchKit: {link}", "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from, [email], msg.as_string())
        # Redact email in production logs
        masked = email[:2] + "***@" + email.split("@")[-1] if "@" in email else "***"
        logger.info("Magic link email sent to %s", masked)
    except Exception:
        logger.exception("Failed to send magic link email to %s", email)
        raise
