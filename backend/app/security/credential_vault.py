"""Local credential vault backed by the OS credential store.

On Windows, the `keyring` package uses Windows Credential Manager. Secrets are
never written to AURA source files, JSON settings, or the project directory.
"""
from __future__ import annotations

import keyring

SERVICE = "JARVIS"
LEGACY_SERVICE = "AURA"
LMS_USERNAME_KEY = "nec_lms_username"
LMS_PASSWORD_KEY = "nec_lms_password"


def set_lms_credentials(username: str, password: str) -> None:
    if not username.strip() or not password:
        raise ValueError("Username and password are required")
    keyring.set_password(SERVICE, LMS_USERNAME_KEY, username.strip())
    keyring.set_password(SERVICE, LMS_PASSWORD_KEY, password)


def get_lms_credentials() -> tuple[str | None, str | None]:
    u = keyring.get_password(SERVICE, LMS_USERNAME_KEY) or keyring.get_password(LEGACY_SERVICE, LMS_USERNAME_KEY)
    p = keyring.get_password(SERVICE, LMS_PASSWORD_KEY) or keyring.get_password(LEGACY_SERVICE, LMS_PASSWORD_KEY)
    return (u, p)


def clear_lms_credentials() -> None:
    for key in (LMS_USERNAME_KEY, LMS_PASSWORD_KEY):
        for svc in (SERVICE, LEGACY_SERVICE):
            try:
                keyring.delete_password(svc, key)
            except keyring.errors.PasswordDeleteError:
                pass


def has_lms_credentials() -> bool:
    username, password = get_lms_credentials()
    return bool(username and password)
