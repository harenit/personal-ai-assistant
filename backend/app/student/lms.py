"""NEC Moodle LMS integration with optional OS-secured credential autofill."""
from __future__ import annotations
import os, re
from pathlib import Path
from app.security.credential_vault import get_lms_credentials, has_lms_credentials

DEFAULT_URL = "https://lms.nec.edu.in/"

def _configured_url() -> str:
    return (
        os.environ.get("AURA_LMS_ASSIGNMENTS_URL")
        or os.environ.get("JARVIS_LMS_ASSIGNMENTS_URL")
        or os.environ.get("AURA_LMS_URL")
        or os.environ.get("JARVIS_LMS_URL", DEFAULT_URL)
    )

def _extract_items(text: str) -> list[dict]:
    lines=[re.sub(r"\s+"," ",x).strip() for x in text.splitlines() if x.strip()]
    items=[]; keywords=("assignment","quiz","test","exam","deadline","due","submission","project")
    for i,line in enumerate(lines):
        if any(k in line.lower() for k in keywords):
            context=" ".join(lines[max(0,i-1):min(len(lines),i+2)])
            items.append({"title":line[:180],"details":context[:400]})
        if len(items)>=30: break
    seen=set(); out=[]
    for x in items:
        key=x["title"].lower()
        if key not in seen: seen.add(key); out.append(x)
    return out

def _login_google(page, username: str, password: str) -> None:
    """Fill Google login when the LMS redirects to Google. User may still need
    to complete MFA/security checks manually; AURA never bypasses them."""
    email = page.locator('input[type="email"]')
    if email.count():
        email.first.fill(username)
        page.get_by_role("button", name=re.compile("Next|Suivant|Weiter|Siguiente", re.I)).first.click()
        page.wait_for_timeout(1200)
    pwd = page.locator('input[type="password"]')
    if pwd.count():
        pwd.first.fill(password)
        page.get_by_role("button", name=re.compile("Next|Sign in|Suivant|Weiter|Siguiente", re.I)).first.click()
        page.wait_for_timeout(2500)

def check_assignments() -> str:
    url=_configured_url()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return "Playwright is not installed. Run: pip install -r backend/requirements.txt && playwright install chromium"
    username, password = get_lms_credentials()
    if not username or not password:
        return "No NEC LMS credentials are configured. Open AURA Settings → Student LMS and save them there."
    try:
        with sync_playwright() as p:
            profile=Path.home()/"AppData"/"Local"/"AURA"/"lms-browser"
            profile.mkdir(parents=True, exist_ok=True)
            # Headed mode allows Google security/MFA prompts to be completed by the user.
            context=p.chromium.launch_persistent_context(str(profile), headless=False)
            page=context.pages[0] if context.pages else context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(1500)
            if "accounts.google.com" in page.url:
                _login_google(page, username, password)
                page.wait_for_timeout(3000)
            # If Google shows a security/MFA step, leave the browser visible for completion.
            if "accounts.google.com" in page.url:
                return "Google authentication needs your attention in the JARVIS browser window. Complete it there, then ask JARVIS to check the LMS again."
            text=page.locator("body").inner_text(timeout=10000)
            items=_extract_items(text)
            context.close()
        if not items:
            return f"I reached the NEC LMS, but couldn't identify assignment/deadline entries. URL: {url}"
        return "Found {} likely student task(s) on the LMS:\n{}".format(len(items), "\n".join(f"- {x['title']} — {x['details']}" for x in items[:10]))
    except Exception as exc:
        return f"I couldn't read the NEC LMS page. Technical reason: {exc}"

def open_lms() -> str:
    url=_configured_url()
    try:
        os.startfile(url)
        return "Opened the NEC LMS."
    except Exception as exc:
        return f"Couldn't open the LMS: {exc}"
