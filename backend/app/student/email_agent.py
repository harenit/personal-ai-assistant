"""Direct email sending agent for AURA.

Supports direct background delivery using smtplib SSL/TLS.
Credentials (email and app password) are secured in Windows Credential Manager via keyring.
If credentials are not yet configured, automatically falls back to opening a pre-filled draft.
"""
from __future__ import annotations

import os
import smtplib
import ssl
import urllib.parse
from email.message import EmailMessage
import keyring

SERVICE = "JARVIS"
LEGACY_SERVICE = "AURA"
EMAIL_USER_KEY = "email_address"
EMAIL_PASS_KEY = "email_app_password"


def set_email_credentials(email: str, app_password: str) -> None:
    keyring.set_password(SERVICE, EMAIL_USER_KEY, email.strip())
    keyring.set_password(SERVICE, EMAIL_PASS_KEY, app_password.strip().replace(" ", ""))


def get_email_credentials() -> tuple[str | None, str | None]:
    email = (
        keyring.get_password(SERVICE, EMAIL_USER_KEY)
        or keyring.get_password(LEGACY_SERVICE, EMAIL_USER_KEY)
        or os.environ.get("JARVIS_EMAIL_USER")
        or os.environ.get("AURA_EMAIL_USER")
    )
    pwd = (
        keyring.get_password(SERVICE, EMAIL_PASS_KEY)
        or keyring.get_password(LEGACY_SERVICE, EMAIL_PASS_KEY)
        or os.environ.get("JARVIS_EMAIL_PASS")
        or os.environ.get("AURA_EMAIL_PASS")
    )
    return email, pwd


def send_email(to_email: str, subject: str = "Message from JARVIS", body: str = "Hi") -> str:
    to_email = to_email.strip()
    subject = subject.strip() or "Message from JARVIS"
    body = body.strip() or "Hi"

    sender, password = get_email_credentials()
    if not sender or not password:
        # Fallback to opening mailto draft
        params = urllib.parse.urlencode({"subject": subject, "body": body})
        mailto_url = f"mailto:{to_email}?{params}"
        try:
            os.startfile(mailto_url)
        except Exception:
            pass
        return (
            f"Draft opened for {to_email}. To send silently in the background, "
            f"configure your Gmail and App Password by saying 'my email is [email] and app password is [16-letter-password]'."
        )

    try:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        context = ssl.create_default_context()
        # Default to Gmail SSL port 465
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=12) as server:
            server.login(sender, password)
            server.send_message(msg)

        return f"Email successfully sent directly to {to_email} with message: \"{body}\"."
    except Exception as exc:
        params = urllib.parse.urlencode({"subject": subject, "body": body})
        try:
            os.startfile(f"mailto:{to_email}?{params}")
        except Exception:
            pass
        return f"Direct transmission failed ({exc}). I opened the pre-filled email draft in your mail app instead."
