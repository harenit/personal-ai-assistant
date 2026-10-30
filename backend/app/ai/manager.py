"""AI manager — the only entry point other modules call for a conversational turn.

Understands natural language via a local AI backend (falling back to
responder.py's simple pattern matching, plus a small regex command parser for
app/file/memory control, if that backend isn't reachable), remembers
conversation history and explicitly-taught preferences via app.memory, and
can request actions — but never executes them itself. Every action request
goes:

    user text -> AIManager (the backend decides, or the fallback parser) ->
    app.security (permission check) -> app.control (executes) -> reply

This project runs entirely for free and fully locally — no API key, no
account, no cloud model. AIManager never talks to a specific backend's HTTP
API directly, only through app.ai.backend.AIBackend, reached via
app.ai.backends.get_backend() — see that module for how another backend
could be added later. Ollama (app.ai.ollama_backend) is the only one
implemented today, with its model chosen via app.ai.config (user-changeable
from Settings, default "llama3.1:8b"). If the current backend isn't
reachable, AURA still opens normally and simply runs in fallback mode
(Settings shows "Local AI not connected." / "Offline").

Closing an application and organizing a folder are both treated as risky: even
with the standing permission granted, AIManager never executes them
immediately — it first asks the user to confirm (via
self._pending_confirmation, checked at the top of the *next* respond() call)
and only executes once they say yes, identically whether the backend is
connected or not.

Remembering/forgetting a preference (app.memory.facts.FactMemory) is not
treated as risky — it's simple, reversible, local text storage the user always
asks for explicitly by saying "remember ..." — so it executes immediately, in
both modes. Remembered facts double as alias resolution: "open my editor"
resolves "editor" to whatever app was last remembered under that name before
calling app.control, in _open()/_switch()/_close_with_confirmation() — a
single choke point shared by both the backend and fallback dispatch paths.

Running a saved automation routine (app.automation.routines.RoutineStore) is
always treated as risky, no exceptions — every routine run goes through the
same self._pending_confirmation mechanism as closing an app or organizing a
folder, listing exactly what it will do before anything runs. Routines are
created/edited from the Automations page in the UI, not through chat; the
backend and the fallback parser can only list and run them.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from app.ai import responder
from app.ai.backend import AIBackendError
from app.ai.backends import get_backend
from app.automation.routines import RoutineStore
from app.control import actions, files, system
from app.history.action_log import ActionLog
from app.memory import config as memory_config
from app.memory.facts import FactMemory
from app.memory.store import ConversationMemory
from app.security.permissions import PermissionManager, Scope
from app.student.lms import check_assignments, open_lms
from app.student.ppt import create_ppt, parse_outline
from app.student.email_agent import send_email, set_email_credentials
from app.student.reminders import set_timer, set_reminder, list_reminders, save_study_note, list_study_notes
from app.student.docs import create_word_document, read_pdf_document
from app.control.files import plan_delete_file, execute_delete_file
from app.academic.deliverables import (
    create_attendance_tracker,
    create_assignment_tracker,
    create_academic_report,
    create_academic_presentation,
    create_study_pack,
)
from app.academic.profile import get_profile_manager
from app.academic.memory import get_academic_memory

SYSTEM_PROMPT = (
    "You are JARVIS, an advanced autonomous AI assistant and academic companion "
    "specifically designed for college and university students. Keep replies concise, "
    "encouraging, and natural — this is spoken aloud and displayed on the student's dashboard. "
    "You understand student life, deadlines, exams, and computer automation. "
    "You can check college LMS assignments and deadlines (e.g. NEC LMS), create real academic deliverables "
    "(PowerPoint .pptx, Word reports .docx, and Excel trackers .xlsx for attendance, marks, and study timetables), "
    "read and summarize PDFs, generate high-yield study packs (flashcards, formula sheets, question banks), "
    "manage study notes, set timers and alerts, send emails, control desktop applications, and safely manage files. "
    "Always assist like an empowering pair programmer and academic mentor. For sensitive or destructive actions, "
    "always request confirmation first."
)

TOOLS = [
    {
        "name": "get_current_time",
        "description": "Get the current local time on the user's computer.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_current_date",
        "description": "Get the current local date on the user's computer.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "check_lms_assignments",
        "description": (
            "Check the user's configured college/LMS for assignments, quizzes, tests, "
            "projects, and deadlines. Uses the local AURA LMS browser profile so "
            "credentials are not stored in source code. If LMS is not configured, "
            "return setup instructions instead of inventing assignments."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "check_lms_notifications",
        "description": "Check the configured LMS page for new notifications, announcements, assignments, and deadline-related items.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "open_lms",
        "description": "Open the configured student LMS in the default browser.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "create_presentation",
        "description": (
            "Create a real PowerPoint .pptx for a student topic. Generate a "
            "well-structured academic presentation with 5-10 slides unless the "
            "user requests another size. Return the exact saved file path."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Presentation topic/title."},
                "slide_count": {"type": "integer", "description": "Number of slides, normally 5-10."},
            },
            "required": ["title"],
        },
    },
    {
        "name": "open_application",
        "description": (
            "Open a desktop application by name — any application actually "
            "installed on this PC, not a fixed list — or a common website "
            "(e.g. 'YouTube', 'Netflix', 'Gmail') or web address, opened in "
            "the default browser. Requires the 'Control applications' "
            "permission in Settings — if it isn't granted, this returns a "
            "denial, not an error; tell the user how to enable it rather "
            "than retrying. If the name doesn't match anything installed or "
            "a known site, this returns a not-found message — don't claim "
            "it opened."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Which application or website to open, e.g. 'notepad', 'spotify', 'youtube'.",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "close_application",
        "description": (
            "Request to close an already-open application (any installed "
            "application, not a fixed list). This never closes anything on "
            "the first call — it always asks the user to confirm first. If "
            "the result starts with 'CONFIRMATION_REQUIRED', relay that "
            "question to the user and wait for their answer; do not call "
            "this tool again for the same request."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Which application to close.",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "switch_window",
        "description": "Bring an already-open application's window to the foreground.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Which application to switch to.",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "open_settings",
        "description": (
            "Open the Windows Settings app. Read-only navigation — this does "
            "not change any setting."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "search_files",
        "description": (
            "Search for files by name (substring match) anywhere on the "
            "user's PC. Read-only. Omit 'root' to search the personal "
            "folders (fast, the common case); pass a personal-folder name, a "
            "drive letter (e.g. 'D'), or a full path to search elsewhere, "
            "including system/program folders."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text to search for in file names."},
                "root": {
                    "type": "string",
                    "description": (
                        "Where to search: omit for the personal folders, or give a "
                        "personal-folder name, drive letter, or full path."
                    ),
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "find_folders",
        "description": (
            "Search for folders by name anywhere on the user's PC. "
            "Read-only. Same 'root' rules as search_files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text to search for in folder names."},
                "root": {"type": "string", "description": "Personal-folder name, drive letter, or full path."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "create_folder",
        "description": "Create a new folder anywhere on the user's PC.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the new folder."},
                "parent": {
                    "type": "string",
                    "description": (
                        "Where to create it: a personal-folder name, drive letter, or "
                        "full path. Defaults to Documents if not said."
                    ),
                },
            },
            "required": ["name"],
        },
    },
    {
        "name": "rename_file",
        "description": (
            "Rename a file the user already has, anywhere on their PC. If "
            "more than one file matches old_name, this returns an "
            "ambiguous-match message instead of guessing which one."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "old_name": {"type": "string"},
                "new_name": {"type": "string"},
                "root": {"type": "string", "description": "Personal-folder name, drive letter, or full path."},
            },
            "required": ["old_name", "new_name"],
        },
    },
    {
        "name": "organize_folder",
        "description": (
            "Sort loose files in a folder into subfolders by type (Images, "
            "Documents, Spreadsheets, Videos, Music, Archives, Installers) — "
            "any folder on the user's PC, not just their personal ones. "
            "Never moves anything on the first call — it always previews the "
            "plan and asks the user to confirm first. If the result starts "
            "with 'CONFIRMATION_REQUIRED', relay it and wait; don't call "
            "this again for the same request."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "root": {"type": "string", "description": "Personal-folder name, drive letter, or full path."}
            },
            "required": ["root"],
        },
    },
    {
        "name": "remember_fact",
        "description": (
            "Remember a preference or fact about the user for future turns, "
            "e.g. their preferred editor or browser. Only call this when the "
            "user explicitly asks you to remember something."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {"type": "string", "description": "Short label, e.g. 'editor', 'browser'."},
                "value": {"type": "string", "description": "The remembered value, e.g. 'VS Code'."},
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "forget_fact",
        "description": "Forget a previously remembered preference or fact by its key.",
        "input_schema": {
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
        },
    },
    {
        "name": "list_routines",
        "description": "List the user's saved automation routines and what each one does.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_routine",
        "description": (
            "Request to run a saved automation routine (e.g. 'Gaming Mode'). "
            "This never runs anything on the first call — it always describes "
            "the steps and asks the user to confirm first. If the result "
            "starts with 'CONFIRMATION_REQUIRED', relay that question to the "
            "user and wait for their answer; do not call this tool again for "
            "the same request."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "The routine's name, e.g. 'Gaming Mode'."}},
            "required": ["name"],
        },
    },
    {
        "name": "create_word_document",
        "description": "Create a structured Word document (.docx) or report on a topic for the student. Saved in Documents/AURA Documents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Title or topic of the document."},
                "topic": {"type": "string", "description": "Subject or specific concepts to cover."},
            },
            "required": ["title"],
        },
    },
    {
        "name": "read_pdf_document",
        "description": "Read, inspect, and summarize a PDF file from Downloads, Documents, Desktop, or an explicit path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Filename or path of the PDF to read, e.g. 'assignment.pdf'."},
            },
            "required": ["query"],
        },
    },
    {
        "name": "delete_file",
        "description": "Request to permanently delete a file. This always asks the user to confirm first before deleting.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_name": {"type": "string", "description": "Name or path of the file to delete."},
                "root": {"type": "string", "description": "Optional folder location, e.g. 'downloads'."},
            },
            "required": ["file_name"],
        },
    },
    {
        "name": "send_email",
        "description": "Send an email directly or open a pre-filled draft to a recipient.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to_email": {"type": "string", "description": "Recipient email address."},
                "subject": {"type": "string", "description": "Email subject."},
                "body": {"type": "string", "description": "Email message body."},
            },
            "required": ["to_email", "body"],
        },
    },
    {
        "name": "set_timer",
        "description": "Set a countdown timer with voice alert.",
        "input_schema": {
            "type": "object",
            "properties": {
                "seconds": {"type": "integer", "description": "Timer duration in seconds."},
                "label": {"type": "string", "description": "Timer description."},
            },
            "required": ["seconds"],
        },
    },
    {
        "name": "set_reminder",
        "description": "Set a reminder for a student task.",
        "input_schema": {
            "type": "object",
            "properties": {
                "label": {"type": "string", "description": "What to remind the student about."},
                "minutes": {"type": "integer", "description": "In how many minutes to trigger."},
            },
            "required": ["label", "minutes"],
        },
    },
    {
        "name": "save_study_note",
        "description": "Save a study note or idea to Documents/JARVIS Notes.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Note title or subject."},
                "content": {"type": "string", "description": "Note text content."},
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "create_excel_tracker",
        "description": "Create an academic Excel spreadsheet tracker (.xlsx) for attendance analysis, marks, or assignment tracking.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tracker_type": {
                    "type": "string",
                    "enum": ["attendance", "assignments", "study_schedule"],
                    "description": "Which type of tracker to generate.",
                },
                "target_percentage": {
                    "type": "number",
                    "description": "Target attendance percentage (e.g. 75.0 or 80.0).",
                },
            },
            "required": ["tracker_type"],
        },
    },
    {
        "name": "create_study_pack",
        "description": "Generate high-yield student revision sheets, flashcards, or practice question banks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "Subject name, e.g. 'DBMS' or 'Operating Systems'."},
                "topic": {"type": "string", "description": "Specific topic or concept."},
                "pack_type": {
                    "type": "string",
                    "enum": ["revision", "flashcards", "questions"],
                    "description": "Type of study material to generate.",
                },
            },
            "required": ["subject", "topic"],
        },
    },
    {
        "name": "get_student_profile",
        "description": "Get current student academic profile (college, department, year, semester, enrolled subjects, exam dates, goals).",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def _to_function_calling_tools(tools: list[dict]) -> list[dict]:
    """Ollama (and most other local/OpenAI-compatible backends) expect
    OpenAI-style function-calling tools
    (`{"type": "function", "function": {"name", "description", "parameters"}}`),
    not the `{"name", "description", "input_schema"}` shape TOOLS is defined
    in above — same JSON Schema underneath, just wrapped differently.
    Converting here (rather than defining tools twice) means TOOLS stays the
    single source of truth for what AURA can do, reusable by any backend
    that speaks this common function-calling shape."""
    return [
        {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"],
            },
        }
        for tool in tools
    ]


FUNCTION_CALLING_TOOLS = _to_function_calling_tools(TOOLS)

# Smaller local models occasionally misbehave around tool-calling in ways
# that have nothing to do with whether app.ai.backends actually parsed
# tool_calls correctly (confirmed separately: real tool calls, e.g. "what
# time is it", come back clean and structured every time). Two observed
# failure shapes, both a model/template quirk rather than anything wrong
# with the request: (1) wrapping an otherwise-normal reply in a stray JSON
# envelope like '{"type": "text", "text": "..."}', and (2) appending a
# hallucinated pseudo tool-call annotation like '(open_application,
# {"name": "X"})' after a normal sentence, without ever populating the real
# tool_calls field. Neither should ever reach the user as spoken/displayed
# text, so every backend reply is cleaned through this before use.
_JSON_WRAPPER_KEYS = ("text", "payload", "content", "message", "response")
# Seen both trailing ("...Settings? (open_application, {"name": "Settings"})")
# and mid-sentence ("...video (open_application, {"name": "YouTube"})? More
# text...") — stripped wherever it appears, not just at the end.
_FAKE_TOOL_CALL = re.compile(r"\(\s*[a-z_][a-z0-9_]*\s*,\s*\{.*?\}\s*\)")


def _extract_wrapped_text(value: object, depth: int = 0) -> str | None:
    """The JSON-envelope quirk isn't a single fixed shape — seen both
    `{"text": "..."}` and nested `{"type": "text", "data": {"text": "..."}}`
    — so this walks a few levels looking for a string under any known
    content-ish key rather than assuming one exact structure."""
    if depth > 3 or not isinstance(value, dict):
        return None
    for key in _JSON_WRAPPER_KEYS:
        found = value.get(key)
        if isinstance(found, str):
            return found
    for nested in value.values():
        found = _extract_wrapped_text(nested, depth + 1)
        if found is not None:
            return found
    return None


def _clean_model_content(content: str) -> str:
    text = content.strip()

    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        parsed = None
    extracted = _extract_wrapped_text(parsed) if isinstance(parsed, dict) else None
    if extracted is not None:
        text = extracted.strip()

    text = _FAKE_TOOL_CALL.sub("", text)
    text = re.sub(r"\s+([?.!,])", r"\1", text)  # no orphaned space before punctuation left behind
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text


_AFFIRMATIVE = {"yes", "yeah", "yep", "yup", "sure", "confirm", "confirmed", "do it", "go ahead", "ok", "okay"}
_NEGATIVE = {"no", "nope", "nah", "cancel", "don't", "dont", "stop", "never mind", "nevermind"}

_OPEN_PATTERN = re.compile(r"^(?:open|launch|start)\s+(.+)$", re.IGNORECASE)
_CLOSE_PATTERN = re.compile(r"^(?:close|quit|exit|stop)\s+(.+)$", re.IGNORECASE)
_SWITCH_PATTERN = re.compile(r"^(?:switch(?: window)? to|focus(?: on)?)\s+(.+)$", re.IGNORECASE)
_SETTINGS_PATTERN = re.compile(r"^open (?:windows |system )?settings$", re.IGNORECASE)
_FIND_FOLDER_PATTERN = re.compile(r"^find (?:a |the )?folder(?: called| named)?\s+(.+)$", re.IGNORECASE)
_SEARCH_FILE_PATTERN = re.compile(r"^(?:find|search for|look for)\s+(?:my\s+)?(.+)$", re.IGNORECASE)
_CREATE_FOLDER_PATTERN = re.compile(
    r"^create (?:a |the )?(?:new )?folder(?: called| named)?\s+([^,]+?)(?:\s+in\s+(\w+))?$", re.IGNORECASE
)
_RENAME_PATTERN = re.compile(r"^rename\s+(.+?)\s+to\s+(.+)$", re.IGNORECASE)
_ORGANIZE_PATTERN = re.compile(r"^organize\s+(?:my\s+)?(\w+)(?:\s+folder)?$", re.IGNORECASE)
_REMEMBER_KV_PATTERN = re.compile(r"^remember (?:that )?my (.+?) is (.+)$", re.IGNORECASE)
_REMEMBER_USE_PATTERN = re.compile(r"^remember (?:that )?i use (.+)$", re.IGNORECASE)
_FORGET_KEY_PATTERN = re.compile(r"^forget (?:that )?my (.+)$", re.IGNORECASE)
_FORGET_USE_PATTERN = re.compile(r"^forget (?:that )?i use (.+)$", re.IGNORECASE)
_LIST_MEMORY_PATTERN = re.compile(r"^what do you (?:remember|know)(?: about me)?\??$", re.IGNORECASE)
_RUN_ROUTINE_PATTERN = re.compile(r"^(?:run|start|activate|trigger)\s+(?:the\s+)?(.+)$", re.IGNORECASE)
_CHECK_LMS_NOTIFICATION_PATTERN = re.compile(r"^(?:check|show|read)(?: my)? (?:lms )?(?:notifications|announcements)\??$", re.IGNORECASE)
_CHECK_LMS_PATTERN = re.compile(r"^(?:check|show|find)(?: my)? (?:lms|assignments|college assignments|pending assignments|deadlines)\??$", re.IGNORECASE)
_CREATE_PPT_PATTERN = re.compile(r"^(?:create|make|generate) (?:a )?(?:ppt|pptx|powerpoint|presentation)(?: on| about| for)?\s+(.+)$", re.IGNORECASE)
_OPEN_LMS_PATTERN = re.compile(r"^(?:open|go to) (?:my )?(?:lms|college portal)$", re.IGNORECASE)
_LIST_ROUTINES_PATTERN = re.compile(
    r"^(?:list|show)(?: my)? (?:routines|automations)\??$"
    r"|^what routines do (?:you|i) have\??$",
    re.IGNORECASE,
)

# Maps a whitelisted app name to the natural-language category most people
# would use for "remember I use X" — lets "Remember I use VS Code" resolve to
# the fact key "editor" without the user having to say "my editor is ..."
APP_CATEGORIES = {
    "notepad": "editor",
    "visual studio code": "editor",
    "vs code": "editor",
    "vscode": "editor",
    "chrome": "browser",
    "google chrome": "browser",
    "discord": "chat app",
    "steam": "game launcher",
    "calculator": "calculator",
    "paint": "image editor",
}


def _is_affirmative(text: str) -> bool:
    lowered = text.lower().strip().rstrip(".!")
    return lowered in _AFFIRMATIVE or any(lowered.startswith(w) for w in _AFFIRMATIVE)


def _is_negative(text: str) -> bool:
    lowered = text.lower().strip().rstrip(".!")
    return lowered in _NEGATIVE or any(lowered.startswith(w) for w in _NEGATIVE)


class AIManager:
    """One instance per backend process — see get_manager() below."""

    def __init__(self) -> None:
        self._memory = ConversationMemory()
        self._facts = FactMemory()
        self._routines = RoutineStore()
        self._permissions = PermissionManager()
        self._history = ActionLog()
        self._pending_confirmation: dict | None = None

    def is_connected(self) -> bool:
        """Whether the current AI backend is reachable right now — checked
        live (not cached), so starting/stopping it takes effect on the very
        next turn without restarting AURA."""
        return get_backend().is_available()

    def get_pending_confirmation(self) -> dict | None:
        """Whether a risky action is awaiting a yes/no, for the frontend's
        confirmation dialog — checked *after* respond() returns, since a
        fresh confirmation may have just been set by that same call."""
        if self._pending_confirmation is None:
            return None
        return {"kind": self._pending_confirmation["kind"], "prompt": self._pending_confirmation["prompt"]}

    def respond(self, text: str) -> str:
        memory_on = memory_config.is_memory_enabled()
        if memory_on:
            self._memory.add_turn("user", text)

        reply = self._handle_pending_confirmation(text)
        if reply is None:
            fast_reply = self._try_control_command(text)
            if fast_reply is not None:
                reply = fast_reply
            elif get_backend().is_available():
                reply = self._respond_with_backend(text, memory_on)
            else:
                reply = self._respond_fallback(text)

        if memory_on:
            self._memory.add_turn("assistant", reply)
        return reply

    # ------------------------------------------------------------------
    # Confirmation flow (shared by both backend and fallback modes, and by
    # every kind of risky action — currently close_application and organize)
    # ------------------------------------------------------------------

    def _handle_pending_confirmation(self, text: str) -> str | None:
        if self._pending_confirmation is None:
            return None
        pending = self._pending_confirmation
        self._pending_confirmation = None

        if _is_affirmative(text):
            if pending["kind"] == "close_application":
                return self._execute_close(pending["name"])
            if pending["kind"] == "organize":
                return self._execute_organize(pending["moves"])
            if pending["kind"] == "run_routine":
                return self._execute_routine(pending["routine"])
            if pending["kind"] == "delete_file":
                return self._execute_delete_file(pending["target"])
            return None
        if _is_negative(text):
            if pending["kind"] == "close_application":
                return f"Okay, I won't close {pending['name']}."
            if pending["kind"] == "organize":
                return "Okay, I won't organize that folder."
            if pending["kind"] == "run_routine":
                return f"Okay, I won't run {pending['routine']['name']}."
            if pending["kind"] == "delete_file":
                return f"Okay, I won't delete {pending['target'].name}."
            return None
        # Ambiguous reply: drop the pending confirmation rather than leave the
        # assistant stuck, and let this message fall through to normal handling.
        return None

    # ------------------------------------------------------------------
    # Fallback mode (backend not reachable): regex command parsing + responder
    # ------------------------------------------------------------------

    def _respond_fallback(self, text: str) -> str:
        control_reply = self._try_control_command(text)
        if control_reply is not None:
            return control_reply
        return responder.respond(text)

    def _try_control_command(self, text: str) -> str | None:
        stripped = text.strip().rstrip(".!?")

        # Direct Email
        email_match = re.search(r"send\s+(?:an?\s+)?(?:mail|email)\s+to\s+([^\s,;]+@[^\s,;]+)(?:.*?(?:stating|saying|message|body)\s+['\"]?(.+?)['\"]?)?$", stripped, re.I)
        if email_match:
            to_addr = email_match.group(1).strip()
            body_text = email_match.group(2) if email_match.group(2) else "Hi"
            return send_email(to_addr, "Message from JARVIS", body_text.strip().strip("'\""))

        # Student Academic Profile
        if re.search(r"\b(?:my\s+profile|student\s+profile|academic\s+profile|show\s+profile)\b", stripped, re.I):
            return self._get_student_profile()

        # Excel Attendance & Assignment Trackers
        if re.search(r"\b(?:attendance\s+tracker|track\s+(?:my\s+)?attendance|attendance\s+sheet|calculate\s+attendance)\b", stripped, re.I):
            return self._create_attendance_tracker()

        if re.search(r"\b(?:assignment\s+tracker|track\s+(?:my\s+)?assignments|marks\s+tracker)\b", stripped, re.I):
            return self._create_assignment_tracker()

        # Study Pack / Flashcards / Question Bank
        sp_match = re.search(r"^(?:generate|create|make)\s+(?:a\s+)?(?:study\s+pack|flashcards?|formula\s+sheet|revision\s+notes?|quiz|questions?)\s+(?:on|for|about)\s+(.+)$", stripped, re.I)
        if sp_match:
            topic = sp_match.group(1).strip()
            ptype = "flashcards" if "flashcard" in stripped.lower() else ("questions" if ("quiz" in stripped.lower() or "question" in stripped.lower()) else "revision")
            return self._create_study_pack("Computer Science", topic, ptype)

        # Word Document Generation
        doc_match = re.search(r"^(?:create|make|write|generate)\s+(?:a\s+)?(?:word\s+)?(?:doc|document|report)(?:\s+(?:on|about|for|titled))?\s*(.+)$", stripped, re.I)
        if doc_match:
            topic = doc_match.group(1).strip()
            return self._create_word_document(topic, topic)

        # PDF Reading & Summarization
        pdf_match = re.search(r"^(?:read|summarize|explain|inspect)\s+(?:the\s+)?(?:pdf|document|file)?\s*([a-zA-Z0-9_\-.]+(?:\.pdf)?)$", stripped, re.I)
        if pdf_match:
            return self._read_pdf(pdf_match.group(1).strip())

        # Safe File Deletion
        del_match = re.search(r"^(?:delete|remove)\s+(?:the\s+)?file\s+(.+)$", stripped, re.I)
        if del_match:
            return self._delete_file_with_confirmation(del_match.group(1).strip(), for_llm=False)

        cred_match = re.search(r"(?:my\s+)?email\s+(?:is\s+)?([^\s,;]+@[^\s,;]+)\s+(?:and\s+)?(?:app\s+password|password)\s+(?:is\s+)?([a-zA-Z0-9 ]+)", stripped, re.I)
        if cred_match:
            set_email_credentials(cred_match.group(1), cred_match.group(2))
            return f"Saved email credentials for {cred_match.group(1)} securely in Windows Credential Manager."

        # Timers & Reminders
        timer_match = re.search(r"(?:set\s+(?:a\s+)?)?timer\s+(?:for\s+)?(\d+)\s*(min(?:ute)?s?|sec(?:ond)?s?|hours?)", stripped, re.I)
        if timer_match:
            qty = int(timer_match.group(1))
            unit = timer_match.group(2).lower()
            secs = qty * 3600 if "hour" in unit else (qty * 60 if "min" in unit else qty)
            return set_timer(secs, label="Timer")

        reminder_match = re.search(r"remind\s+me\s+(?:in\s+(\d+)\s*(min(?:ute)?s?|hours?)\s+to\s+(.+)|to\s+(.+?)\s+in\s+(\d+)\s*(min(?:ute)?s?|hours?))", stripped, re.I)
        if reminder_match:
            if reminder_match.group(1):
                qty = int(reminder_match.group(1))
                unit = reminder_match.group(2).lower()
                label = reminder_match.group(3).strip()
            else:
                label = reminder_match.group(4).strip()
                qty = int(reminder_match.group(5))
                unit = reminder_match.group(6).lower()
            mins = qty * 60 if "hour" in unit else qty
            return set_reminder(label, mins)

        if re.search(r"\b(list\s+reminders|show\s+(?:my\s+)?reminders|active\s+timers|show\s+timers)\b", stripped, re.I):
            return list_reminders()

        # Study Notes
        note_match = re.search(r"(?:save|take)\s+(?:a\s+)?note\s+(?:on|about|titled)?\s*([^:]+?)(?::\s*|\s+saying\s+)(.+)", stripped, re.I)
        if note_match:
            return save_study_note(note_match.group(1).strip(), note_match.group(2).strip())

        if re.search(r"\b(list\s+notes|show\s+(?:my\s+)?notes|study\s+notes)\b", stripped, re.I):
            return list_study_notes()

        if re.search(r"\b(what('s| is)? the time|current time|tell me the time|time is it)\b", stripped, re.I):
            now = datetime.now().strftime("%I:%M %p").lstrip("0")
            return f"The current time is {now}."

        if re.search(r"\b(what('s| is)? the date|today('s)? date|current date|what day is it)\b", stripped, re.I):
            today = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {today}."

        if _LIST_MEMORY_PATTERN.match(stripped):
            return self._list_facts()

        if _LIST_ROUTINES_PATTERN.match(stripped):
            return self._list_routines()

        match = _RUN_ROUTINE_PATTERN.match(stripped)
        if match:
            candidate = match.group(1).strip()
            if self._routines.get_by_name(candidate) is not None:
                return self._request_run_routine(candidate, for_llm=False)
            # Not a known routine name (e.g. "start chrome") — fall through so
            # the app-open pattern below still gets a chance to handle it.

        match = _REMEMBER_KV_PATTERN.match(stripped)
        if match:
            return self._remember_fact(match.group(1).strip().lower(), match.group(2).strip())

        match = _REMEMBER_USE_PATTERN.match(stripped)
        if match:
            app_name = match.group(1).strip()
            category = APP_CATEGORIES.get(app_name.lower(), app_name.lower())
            return self._remember_fact(category, app_name)

        match = _FORGET_KEY_PATTERN.match(stripped)
        if match:
            return self._forget_fact(match.group(1).strip().lower())

        match = _FORGET_USE_PATTERN.match(stripped)
        if match:
            app_name = match.group(1).strip()
            category = APP_CATEGORIES.get(app_name.lower(), app_name.lower())
            return self._forget_fact(category)

        if _CHECK_LMS_NOTIFICATION_PATTERN.match(stripped):
            return self._check_lms()

        if _CHECK_LMS_PATTERN.match(stripped):
            return self._check_lms()

        match = _CREATE_PPT_PATTERN.match(stripped)
        if match:
            return self._create_presentation(match.group(1).strip(), 7)

        if _OPEN_LMS_PATTERN.match(stripped):
            return self._open_lms()

        if _SETTINGS_PATTERN.match(stripped):
            return self._open_settings()

        match = _CLOSE_PATTERN.match(stripped)
        if match:
            return self._close_with_confirmation(match.group(1).strip(), for_llm=False)

        match = _ORGANIZE_PATTERN.match(stripped)
        if match:
            return self._organize_with_confirmation(match.group(1).strip(), for_llm=False)

        match = _CREATE_FOLDER_PATTERN.match(stripped)
        if match:
            name = match.group(1).strip()
            parent = (match.group(2) or "documents").strip()
            return self._create_folder(name, parent)

        match = _RENAME_PATTERN.match(stripped)
        if match:
            return self._rename_file(match.group(1).strip(), match.group(2).strip())

        match = _FIND_FOLDER_PATTERN.match(stripped)
        if match:
            return self._find_folders(match.group(1).strip())

        match = _OPEN_PATTERN.match(stripped)
        if match:
            return self._open(match.group(1).strip())

        match = _SWITCH_PATTERN.match(stripped)
        if match:
            return self._switch(match.group(1).strip())

        match = _SEARCH_FILE_PATTERN.match(stripped)
        if match:
            return self._search_files(match.group(1).strip())

        return None

    # ------------------------------------------------------------------
    # Backend mode (the current AI backend — Ollama today, see app.ai.backends)
    # ------------------------------------------------------------------

    def _build_system_prompt(self) -> str:
        if not memory_config.is_memory_enabled():
            return SYSTEM_PROMPT
        facts = self._facts.all()
        if not facts:
            return SYSTEM_PROMPT
        facts_lines = "\n".join(f"- {f['key']}: {f['value']}" for f in facts)
        return SYSTEM_PROMPT + f"\n\nPreferences already remembered about this user:\n{facts_lines}"

    def _select_relevant_tools(self, query: str) -> list[dict] | None:
        q = query.lower()
        tool_keywords = {
            "get_current_time": ["time", "clock", "hour"],
            "get_current_date": ["date", "day", "today", "year", "month"],
            "check_lms_assignments": ["lms", "moodle", "assignment", "assignments", "quiz", "quizzes", "test", "exam", "due", "deadline", "college"],
            "check_lms_notifications": ["lms", "notification", "announcements", "notice"],
            "open_lms": ["lms", "moodle", "college"],
            "create_presentation": ["ppt", "presentation", "powerpoint", "slide", "slides"],
            "open_application": ["open", "launch", "start", "run", "app", "application", "browser", "calc", "calculator", "notepad", "chrome", "vscode", "spotify", "youtube"],
            "close_application": ["close", "exit", "quit", "terminate", "kill"],
            "switch_window": ["switch", "focus", "window"],
            "open_settings": ["settings", "preferences"],
            "search_files": ["search", "find", "file", "files"],
            "find_folders": ["folder", "folders", "directory"],
            "create_folder": ["create folder", "make folder", "mkdir"],
            "rename_file": ["rename"],
            "organize_folder": ["organize", "sort"],
            "remember_fact": ["remember", "preference", "favorite"],
            "forget_fact": ["forget"],
            "list_routines": ["routines", "routine", "automations"],
            "run_routine": ["routine", "gaming mode", "work mode", "study mode"],
            "check_system_performance": ["performance", "cpu", "ram", "specs", "hardware", "battery", "disk", "usage"],
            "create_word_document": ["document", "doc", "docx", "word", "report", "paper", "write a document"],
            "read_pdf_document": ["pdf", "read pdf", "summarize pdf", "syllabus", "extract"],
            "delete_file": ["delete", "remove file", "trash"],
            "send_email": ["email", "mail", "send email", "message"],
            "set_timer": ["timer", "countdown"],
            "set_reminder": ["remind", "reminder"],
            "save_study_note": ["note", "notes", "study note"],
            "create_excel_tracker": ["excel", "xlsx", "spreadsheet", "attendance", "attendance tracker", "marks", "grade tracker"],
            "create_study_pack": ["flashcard", "flashcards", "study pack", "formula sheet", "question bank", "quiz", "mcq", "viva"],
            "get_student_profile": ["profile", "my profile", "academic profile", "my subjects", "my degree", "my college"],
        }
        tool_map = {t["function"]["name"]: t for t in FUNCTION_CALLING_TOOLS}
        selected = []
        for tool_name, keywords in tool_keywords.items():
            if any(kw in q for kw in keywords):
                if tool_name in tool_map and tool_map[tool_name] not in selected:
                    selected.append(tool_map[tool_name])
        return selected[:4] if selected else None

    def _respond_with_backend(self, text: str, memory_on: bool) -> str:
        backend = get_backend()
        messages = self._memory.recent_messages() if memory_on else [{"role": "user", "content": text}]
        full_messages = [{"role": "system", "content": self._build_system_prompt()}] + messages

        active_tools = self._select_relevant_tools(text)

        try:
            message = backend.chat(full_messages, tools=active_tools)

            # Bounded rather than open-ended — a local model is less
            # predictable about ever actually stopping tool use on its own,
            # so this is a hard backstop against an infinite tool-call loop.
            for _ in range(6):
                tool_calls = message.get("tool_calls")
                if not tool_calls:
                    break
                full_messages.append({"role": "assistant", "content": message.get("content", ""), "tool_calls": tool_calls})
                for call in tool_calls:
                    fn = call.get("function", {})
                    result = self._run_tool(fn.get("name", ""), fn.get("arguments") or {})
                    full_messages.append({"role": "tool", "content": result})
                message = backend.chat(full_messages, tools=active_tools)
        except AIBackendError:
            # Fall back cleanly so the user receives a helpful reply
            fallback = self._respond_fallback(text)
            if fallback and not fallback.startswith("I heard you say"):
                return fallback
            return "I heard you, but the local model is taking a moment to process. How else can I help?"

        return _clean_model_content(message.get("content") or "")

    def _run_tool(self, name: str, tool_input: dict) -> str:
        if name == "get_current_time":
            return datetime.now().strftime("%I:%M %p").lstrip("0")
        if name == "get_current_date":
            return datetime.now().strftime("%A, %B %d, %Y")
        if name == "check_lms_assignments":
            return self._check_lms()
        if name == "open_lms":
            return self._open_lms()
        if name == "check_lms_notifications":
            return self._check_lms()
        if name == "create_presentation":
            return self._create_presentation(tool_input.get("title", ""), int(tool_input.get("slide_count") or 7))
        if name == "open_application":
            return self._open(tool_input.get("name", ""))
        if name == "close_application":
            return self._close_with_confirmation(tool_input.get("name", ""), for_llm=True)
        if name == "switch_window":
            return self._switch(tool_input.get("name", ""))
        if name == "open_settings":
            return self._open_settings()
        if name == "search_files":
            return self._search_files(tool_input.get("query", ""), tool_input.get("root"))
        if name == "find_folders":
            return self._find_folders(tool_input.get("query", ""), tool_input.get("root"))
        if name == "create_folder":
            return self._create_folder(tool_input.get("name", ""), tool_input.get("parent", "documents"))
        if name == "rename_file":
            return self._rename_file(
                tool_input.get("old_name", ""), tool_input.get("new_name", ""), tool_input.get("root")
            )
        if name == "organize_folder":
            return self._organize_with_confirmation(tool_input.get("root", ""), for_llm=True)
        if name == "remember_fact":
            return self._remember_fact(tool_input.get("key", ""), tool_input.get("value", ""))
        if name == "forget_fact":
            return self._forget_fact(tool_input.get("key", ""))
        if name == "list_routines":
            return self._list_routines()
        if name == "run_routine":
            return self._request_run_routine(tool_input.get("name", ""), for_llm=True)
        if name == "create_word_document":
            return self._create_word_document(tool_input.get("title", ""), tool_input.get("topic", ""))
        if name == "read_pdf_document":
            return self._read_pdf(tool_input.get("query", ""))
        if name == "delete_file":
            return self._delete_file_with_confirmation(tool_input.get("file_name", ""), tool_input.get("root"), for_llm=True)
        if name == "send_email":
            return send_email(tool_input.get("to_email", ""), tool_input.get("subject", "Message from JARVIS"), tool_input.get("body", "Hi"))
        if name == "set_timer":
            return set_timer(int(tool_input.get("seconds", 60)), label=tool_input.get("label", "Timer"))
        if name == "set_reminder":
            return set_reminder(tool_input.get("label", "Reminder"), int(tool_input.get("minutes", 5)))
        if name == "save_study_note":
            return save_study_note(tool_input.get("title", "Study Note"), tool_input.get("content", ""))
        if name == "create_excel_tracker":
            kind = tool_input.get("tracker_type", "attendance")
            target_pct = float(tool_input.get("target_percentage") or 75.0)
            if kind == "assignments":
                return self._create_assignment_tracker()
            return self._create_attendance_tracker(target_pct)
        if name == "create_study_pack":
            return self._create_study_pack(
                tool_input.get("subject", "Computer Science"),
                tool_input.get("topic", "General Topic"),
                tool_input.get("pack_type", "revision"),
            )
        if name == "get_student_profile":
            return self._get_student_profile()
        return f"Unknown tool: {name}"

    # ------------------------------------------------------------------
    # Student tools
    # ------------------------------------------------------------------
    def _check_lms(self) -> str:
        if not self._permissions.is_granted(Scope.STUDENT_LMS):
            return "Permission denied: enable the 'Student LMS access' permission in Settings."
        result = check_assignments()
        self._history.record("check_lms", "assignments", result)
        return result

    def _open_lms(self) -> str:
        if not self._permissions.is_granted(Scope.STUDENT_LMS):
            return "Permission denied: enable the 'Student LMS access' permission in Settings."
        result = open_lms()
        self._history.record("open_lms", "", result)
        return result

    def _create_presentation(self, title: str, slide_count: int = 7) -> str:
        if not self._permissions.is_granted(Scope.CREATE_PPT):
            return "Permission denied: enable the 'Create PowerPoint files' permission in Settings."
        title = title.strip()
        if not title:
            return "Tell me the topic for the presentation."
        slide_count = min(max(slide_count, 3), 12)
        outline = None
        backend = get_backend()
        if backend.is_available():
            prompt = (f"Create a JSON-only academic PowerPoint outline for '{title}'. "
                      f"Use exactly {slide_count} slides. Return an array of objects with "
                      f"keys title and bullets. Each slide should have 3-5 concise, factual bullets. "
                      f"Do not include markdown or code fences.")
            try:
                msg = backend.chat([{"role":"user","content":prompt}], tools=[])
                outline = parse_outline(msg.get("content",""), title, slide_count)
            except Exception:
                outline = None
        path = create_ppt(title, outline)
        self._history.record("create_presentation", title, path)
        return f"Created the PowerPoint with {len(outline or [])} slides: {path}"

    def _create_word_document(self, title: str, topic: str = "") -> str:
        title = title.strip()
        if not title:
            return "Please provide a title or topic for the document."
        path = create_word_document(title, topic)
        self._history.record("create_word_document", title, path)
        return f"Created your Word document: {path}"

    def _create_attendance_tracker(self, target_pct: float = 75.0) -> str:
        prof = get_profile_manager().get_profile()
        path = create_attendance_tracker(prof.subjects, target_pct)
        self._history.record("create_excel_tracker", "attendance", path)
        return f"Generated your Attendance Tracker spreadsheet with shortage analysis and targets: {path}"

    def _create_assignment_tracker(self) -> str:
        path = create_assignment_tracker()
        self._history.record("create_excel_tracker", "assignments", path)
        return f"Generated your Semester Assignment and Marks Tracker spreadsheet: {path}"

    def _create_study_pack(self, subject: str, topic: str, pack_type: str = "revision") -> str:
        path = create_study_pack(subject, topic, pack_type)
        self._history.record("create_study_pack", f"{subject}: {topic}", path)
        return f"Generated your {pack_type} study pack for {subject} ({topic}): {path}"

    def _get_student_profile(self) -> str:
        p = get_profile_manager().get_profile()
        return (
            f"Student Academic Profile:\n"
            f"- Name: {p.name}\n"
            f"- Institution: {p.college}\n"
            f"- Department: {p.department} ({p.academic_year}, {p.semester})\n"
            f"- Active Courses: {', '.join(p.subjects)}\n"
            f"- Academic Goals: {'; '.join(p.academic_goals)}"
        )

    def _read_pdf(self, query: str) -> str:
        if not self._permissions.is_granted(Scope.FS_READ):
            return self._fs_read_denied()
        result = read_pdf_document(query)
        self._history.record("read_pdf", query, result[:80])
        return result

    def _delete_file_with_confirmation(self, name_or_path: str, root: str | None = None, *, for_llm: bool = False) -> str:
        if not self._permissions.is_granted(Scope.FS_WRITE):
            return self._fs_write_denied()
        target, prompt = plan_delete_file(name_or_path, root)
        if target is None:
            return prompt
        self._pending_confirmation = {"kind": "delete_file", "target": target, "prompt": prompt}
        if for_llm:
            return (
                f"CONFIRMATION_REQUIRED: {prompt} Ask the user to confirm before "
                f"deleting anything — do not say it is deleted. Their next message will "
                f"be the answer; you do not need to call this tool again."
            )
        return f"{prompt} Say yes to confirm."

    def _execute_delete_file(self, target: Path) -> str:
        if not self._permissions.is_granted(Scope.FS_WRITE):
            return "Permission was turned off, so I didn't delete the file."
        result = execute_delete_file(target)
        self._history.record("delete_file", str(target), result)
        return result

    # ------------------------------------------------------------------
    # Memory helpers
    # ------------------------------------------------------------------

    def _resolve_alias(self, name: str) -> str:
        """If `name` looks like 'my X' and a fact for X is remembered, returns
        the remembered value instead (e.g. 'my editor' -> 'VS Code')."""
        if not memory_config.is_memory_enabled():
            return name
        stripped = name.strip().lower()
        if stripped.startswith("my "):
            key = stripped[3:].strip()
            remembered = self._facts.recall(key)
            if remembered:
                return remembered
        return name

    def _remember_fact(self, key: str, value: str) -> str:
        if not memory_config.is_memory_enabled():
            return "Memory is turned off in Settings, so I won't remember that."
        if not key or not value:
            return "I need both what to remember and its value."
        self._facts.remember(key, value)
        return f"Got it, I'll remember that your {key} is {value}."

    def _forget_fact(self, key: str) -> str:
        if not memory_config.is_memory_enabled():
            return "Memory is turned off in Settings."
        if self._facts.forget(key):
            return f"Okay, I've forgotten your {key}."
        return f"I didn't have anything remembered for '{key}'."

    def _list_facts(self) -> str:
        facts = self._facts.all()
        if not facts:
            return "I don't have anything remembered about you yet."
        lines = ", ".join(f"your {f['key']} is {f['value']}" for f in facts)
        return f"Here's what I remember: {lines}."

    # ------------------------------------------------------------------
    # Shared action helpers (permission-gated; the only path into app.control)
    # ------------------------------------------------------------------

    def _app_permission_denied(self) -> str:
        return "Permission denied: the 'Control applications' permission is not enabled. Enable it in Settings."

    def _fs_read_denied(self) -> str:
        return "Permission denied: the 'Search files' permission is not enabled. Enable it in Settings."

    def _fs_write_denied(self) -> str:
        return "Permission denied: the 'Manage files' permission is not enabled. Enable it in Settings."

    def _open(self, name: str) -> str:
        name = self._resolve_alias(name)
        if not self._permissions.is_granted(Scope.CONTROL_LAUNCH_APP):
            return self._app_permission_denied()
        result = actions.open_application(name)
        self._history.record("open_app", name, result)
        return result

    def _switch(self, name: str) -> str:
        name = self._resolve_alias(name)
        if not self._permissions.is_granted(Scope.CONTROL_LAUNCH_APP):
            return self._app_permission_denied()
        result = actions.switch_window(name)
        self._history.record("switch_window", name, result)
        return result

    def _open_settings(self) -> str:
        if not self._permissions.is_granted(Scope.CONTROL_LAUNCH_APP):
            return self._app_permission_denied()
        result = actions.open_windows_settings()
        self._history.record("open_settings", "", result)
        return result

    def _close_with_confirmation(self, name: str, *, for_llm: bool) -> str:
        name = self._resolve_alias(name)
        if not self._permissions.is_granted(Scope.CONTROL_LAUNCH_APP):
            return self._app_permission_denied()

        prompt = f"Do you want me to close {name}?"
        self._pending_confirmation = {"kind": "close_application", "name": name, "prompt": prompt}
        if for_llm:
            return (
                f"CONFIRMATION_REQUIRED: The user has not confirmed yet. Ask them "
                f"out loud whether they want to close {name} — do not say it is "
                f"closed. Their next message will be the answer; you do not need "
                f"to call this tool again."
            )
        return f"Do you want me to close {name}? Say yes to confirm."

    def _execute_close(self, name: str) -> str:
        if not self._permissions.is_granted(Scope.CONTROL_LAUNCH_APP):
            return "That permission was turned off before I could confirm, so I didn't close anything."
        result = actions.close_application(name)
        self._history.record("close_app", name, result)
        return result

    def _search_files(self, query: str, root: str | None = None) -> str:
        if not self._permissions.is_granted(Scope.FS_READ):
            return self._fs_read_denied()
        matches = files.search_files(query, root)
        if matches is None:
            return f"I couldn't find a location called '{root}'."
        if not matches:
            return f"I couldn't find any files matching '{query}'."
        names = [Path(p).name for p in matches[:8]]
        listing = ", ".join(names)
        more = f", and {len(matches) - 8} more" if len(matches) > 8 else ""
        return f"Found {len(matches)} file(s) matching '{query}': {listing}{more}."

    def _find_folders(self, query: str, root: str | None = None) -> str:
        if not self._permissions.is_granted(Scope.FS_READ):
            return self._fs_read_denied()
        matches = files.find_folders(query, root)
        if matches is None:
            return f"I couldn't find a location called '{root}'."
        if not matches:
            return f"I couldn't find any folders matching '{query}'."
        names = [Path(p).name for p in matches[:8]]
        listing = ", ".join(names)
        return f"Found {len(matches)} folder(s) matching '{query}': {listing}."

    def _create_folder(self, name: str, parent: str = "documents") -> str:
        if not self._permissions.is_granted(Scope.FS_WRITE):
            return self._fs_write_denied()
        result = files.create_folder(name, parent)
        self._history.record("create_folder", f"{name} in {parent}", result)
        return result

    def _rename_file(self, old_name: str, new_name: str, root: str | None = None) -> str:
        if not self._permissions.is_granted(Scope.FS_WRITE):
            return self._fs_write_denied()
        result = files.rename_file(old_name, new_name, root)
        self._history.record("rename_file", f"{old_name} -> {new_name}", result)
        return result

    def _organize_with_confirmation(self, root: str, *, for_llm: bool) -> str:
        if not self._permissions.is_granted(Scope.FS_WRITE):
            return self._fs_write_denied()

        moves = files.plan_organize(root)
        label = root.title() if root.strip().lower() in files.SAFE_ROOTS else root
        if not moves:
            return f"There's nothing in {label} that I know how to organize."

        categories = sorted({dest.parent.name for _, dest in moves})
        summary = f"I found {len(moves)} file(s) I can sort into {', '.join(categories)} folders in {label}."
        prompt = f"{summary} Do you want me to go ahead?"
        self._pending_confirmation = {"kind": "organize", "moves": moves, "prompt": prompt}
        if for_llm:
            return (
                f"CONFIRMATION_REQUIRED: {summary} Ask the user to confirm before "
                f"moving anything — do not say it's done. Their next message will "
                f"be the answer; you do not need to call this tool again."
            )
        return f"{summary} Do you want me to go ahead? Say yes to confirm."

    def _execute_organize(self, moves: list[tuple[Path, Path]]) -> str:
        if not self._permissions.is_granted(Scope.FS_WRITE):
            return "That permission was turned off before I could confirm, so I didn't move anything."
        result = files.execute_organize(moves)
        self._history.record("organize_folder", f"{len(moves)} file(s)", result)
        return result

    def _open_folder(self, root: str) -> str:
        if not self._permissions.is_granted(Scope.FS_READ):
            return self._fs_read_denied()
        return files.open_folder(root)

    def _check_performance(self) -> str:
        return system.check_performance()

    # ------------------------------------------------------------------
    # Automation routines (always confirmed before running — see
    # self._pending_confirmation, shared with close/organize above)
    # ------------------------------------------------------------------

    def _describe_step(self, step: dict) -> str:
        step_type, target = step["type"], step.get("target", "")
        if step_type == "open_app":
            return f"open {target}"
        if step_type == "switch_window":
            return f"switch to {target}"
        if step_type == "open_settings":
            return "open Settings"
        if step_type == "open_folder":
            return f"open the {target.title()} folder"
        if step_type == "check_performance":
            return "check PC performance"
        return step_type

    def _list_routines(self) -> str:
        routines = self._routines.all()
        if not routines:
            return "You don't have any automation routines yet. Create one from the Automations page."
        lines = [
            f"{r['name']} ({', '.join(self._describe_step(s) for s in r['steps'])})" for r in routines
        ]
        return "Here are your routines: " + "; ".join(lines) + "."

    def _request_run_routine(self, identifier: str, *, for_llm: bool) -> str:
        routine = self._routines.get_by_name(identifier) or self._routines.get(identifier)
        if routine is None:
            return f"I don't have a routine called '{identifier}'. Say 'what routines do I have?' to see them."
        if not routine["steps"]:
            return f"{routine['name']} doesn't have any steps yet."

        step_summary = ", then ".join(self._describe_step(s) for s in routine["steps"])
        prompt = f"Running {routine['name']} will: {step_summary}. Do you want me to go ahead?"
        self._pending_confirmation = {"kind": "run_routine", "routine": routine, "prompt": prompt}
        if for_llm:
            return (
                f"CONFIRMATION_REQUIRED: Running '{routine['name']}' will: "
                f"{step_summary}. Ask the user to confirm out loud before "
                f"running anything — do not say it's done. Their next message "
                f"will be the answer; you do not need to call this tool again."
            )
        return f"Running {routine['name']} will: {step_summary}. Say yes to confirm."

    def request_run_routine(self, identifier: str) -> str:
        """Public entry point for the Automations page's Run button — shares
        the exact same confirm-then-run path as "run <routine>" in chat."""
        return self._request_run_routine(identifier, for_llm=False)

    def _execute_routine(self, routine: dict) -> str:
        results = [self._execute_step(step) for step in routine["steps"]]
        summary = f"Ran {routine['name']}. " + " ".join(results)
        self._history.record("run_routine", routine["name"], summary)
        return summary

    def _execute_step(self, step: dict) -> str:
        step_type = step["type"]
        target = step.get("target", "")
        if step_type == "open_app":
            return self._open(target)
        if step_type == "switch_window":
            return self._switch(target)
        if step_type == "open_settings":
            return self._open_settings()
        if step_type == "open_folder":
            return self._open_folder(target)
        if step_type == "check_performance":
            return self._check_performance()
        return f"Unknown step: {step_type}."


_manager: AIManager | None = None


def get_manager() -> AIManager:
    global _manager
    if _manager is None:
        _manager = AIManager()
    return _manager
