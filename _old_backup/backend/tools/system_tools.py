import os
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Any
from backend.tools.base import BaseTool
from backend.permissions.models import RiskLevel
from backend.config.settings import settings

# Mapping of common names to executable names or standard paths
APP_EXECUTABLE_MAP = {
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "notepad": "notepad.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "code": "code.cmd",
    "vscode": "code.cmd",
    "visual studio code": "code.cmd",
    "powerpoint": "powerpnt.exe",
    "powerpnt": "powerpnt.exe",
    "word": "winword.exe",
    "winword": "winword.exe",
    "paint": "mspaint.exe",
    "mspaint": "mspaint.exe"
}

STANDARD_PROGRAM_PATHS = [
    r"C:\Program Files\Microsoft Office\root\Office16",
    r"C:\Program Files (x86)\Microsoft Office\root\Office16",
    r"C:\Program Files\Google\Chrome\Application",
    r"C:\Program Files (x86)\Microsoft\Edge\Application",
    r"C:\Windows\System32",
    r"C:\Windows"
]

def find_executable(app_name: str) -> tuple[bool, str]:
    normalized = app_name.strip().lower()
    exe_name = APP_EXECUTABLE_MAP.get(normalized, f"{normalized}.exe")

    # 1. Check via PATH
    which_path = shutil.which(exe_name)
    if which_path:
        return True, which_path

    # 2. Check standard known paths
    for base in STANDARD_PROGRAM_PATHS:
        candidate = Path(base) / exe_name
        if candidate.exists():
            return True, str(candidate)

    # 3. Check AppData local for VS Code
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        vscode_candidate = Path(local_app_data) / "Programs" / "Microsoft VS Code" / "Code.exe"
        if "code" in normalized and vscode_candidate.exists():
            return True, str(vscode_candidate)

    # 4. For system built-ins like calc.exe, explorer.exe, notepad.exe, Windows runs them directly via shell lookup
    if exe_name in ["calc.exe", "notepad.exe", "explorer.exe", "mspaint.exe"]:
        return True, exe_name

    return False, exe_name

class OpenApplicationTool(BaseTool):
    name = "open_application"
    description = "Launch an allowlisted Windows desktop application such as Calculator, Notepad, File Explorer, Microsoft Edge, Google Chrome, VS Code, PowerPoint, Word, or Paint."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "application_name": {
                "type": "string",
                "description": "Name of the desktop application to open (e.g. 'calculator', 'notepad', 'edge', 'chrome', 'vscode', 'powerpoint', 'word', 'explorer')"
            }
        },
        "required": ["application_name"]
    }

    def execute(self, application_name: str, **kwargs) -> dict[str, Any]:
        clean_name = application_name.strip().lower()

        # Validate against allowlist
        allowed = any(clean_name == allowed_app or allowed_app in clean_name for allowed_app in settings.ALLOWED_APP_NAMES)
        if not allowed:
            return {
                "success": False,
                "action": "open_application",
                "target": application_name,
                "message": f"Application '{application_name}' is not in the authorized application allowlist."
            }

        found, exe_path = find_executable(clean_name)
        if not found:
            return {
                "success": False,
                "action": "open_application",
                "target": application_name,
                "message": f"Application '{application_name}' ({exe_path}) was not found on this Windows system."
            }

        try:
            # Safely launch application without shell=True
            subprocess.Popen([exe_path], close_fds=True)
            return {
                "success": True,
                "action": "open_application",
                "target": application_name,
                "executable": exe_path,
                "message": f"Successfully launched {application_name} on your Windows computer."
            }
        except Exception as e:
            return {
                "success": False,
                "action": "open_application",
                "target": application_name,
                "message": f"Failed to launch {application_name}: {str(e)}"
            }

class CloseApplicationTool(BaseTool):
    name = "close_application"
    description = "Close an open allowlisted desktop application safely (e.g. calculator, notepad)."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "application_name": {
                "type": "string",
                "description": "Name of the application to close (e.g. 'calculator', 'notepad')"
            }
        },
        "required": ["application_name"]
    }

    def execute(self, application_name: str, **kwargs) -> dict[str, Any]:
        clean_name = application_name.strip().lower()
        exe_name = APP_EXECUTABLE_MAP.get(clean_name, f"{clean_name}.exe")

        # Allowlist check
        allowed = any(clean_name == allowed_app or allowed_app in clean_name for allowed_app in settings.ALLOWED_APP_NAMES)
        if not allowed:
            return {
                "success": False,
                "action": "close_application",
                "target": application_name,
                "message": f"Application '{application_name}' is not authorized to close."
            }

        try:
            # Use taskkill safely
            result = subprocess.run(
                ["taskkill", "/IM", exe_name, "/F"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return {
                    "success": True,
                    "action": "close_application",
                    "target": application_name,
                    "message": f"Successfully closed {application_name}."
                }
            else:
                return {
                    "success": False,
                    "action": "close_application",
                    "target": application_name,
                    "message": f"No running instance of {application_name} was found."
                }
        except Exception as e:
            return {
                "success": False,
                "action": "close_application",
                "target": application_name,
                "message": f"Could not close {application_name}: {str(e)}"
            }

class OpenUrlTool(BaseTool):
    name = "open_url"
    description = "Open an authorized HTTP or HTTPS URL in the default web browser (e.g. YouTube tutorial, educational website, research article)."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The web URL to open (must start with http:// or https://)"
            }
        },
        "required": ["url"]
    }

    def execute(self, url: str, **kwargs) -> dict[str, Any]:
        clean_url = url.strip()
        if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
            return {
                "success": False,
                "action": "open_url",
                "target": url,
                "message": "Invalid URL protocol. Only http:// and https:// URLs are permitted."
            }

        try:
            opened = webbrowser.open(clean_url)
            return {
                "success": True,
                "action": "open_url",
                "target": clean_url,
                "message": f"Opened {clean_url} in your default web browser."
            }
        except Exception as e:
            return {
                "success": False,
                "action": "open_url",
                "target": clean_url,
                "message": f"Failed to open URL: {str(e)}"
            }

class OpenGeneratedFileTool(BaseTool):
    name = "open_generated_file"
    description = "Open a generated document, presentation (.pptx), study guide, or report in its default Windows desktop application."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Relative or absolute path to the generated file to open (e.g. in generated/presentations/)"
            }
        },
        "required": ["file_path"]
    }

    def execute(self, file_path: str, **kwargs) -> dict[str, Any]:
        clean_path = Path(file_path).resolve()
        
        # Security validation: make sure the file is within project directory
        project_root = settings.PROJECT_ROOT.resolve()
        try:
            clean_path.relative_to(project_root)
        except ValueError:
            # Also allow files in user's temp or documents if generated
            pass

        if not clean_path.exists():
            # Check inside generated/presentations
            alt_path = settings.PRESENTATIONS_DIR / Path(file_path).name
            if alt_path.exists():
                clean_path = alt_path
            else:
                return {
                    "success": False,
                    "action": "open_generated_file",
                    "target": file_path,
                    "message": f"File '{file_path}' does not exist on disk."
                }

        try:
            os.startfile(str(clean_path))
            return {
                "success": True,
                "action": "open_generated_file",
                "target": str(clean_path),
                "message": f"Opened '{clean_path.name}' in its default application."
            }
        except Exception as e:
            return {
                "success": False,
                "action": "open_generated_file",
                "target": str(clean_path),
                "message": f"Could not launch file '{clean_path.name}': {str(e)}"
            }

class OpenFolderTool(BaseTool):
    name = "open_folder"
    description = "Open a designated safe folder (such as generated presentations, uploaded documents, or project data) in Windows File Explorer."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "folder_name": {
                "type": "string",
                "description": "Folder to open ('presentations', 'documents', 'uploads', 'data', or relative path)"
            }
        },
        "required": ["folder_name"]
    }

    def execute(self, folder_name: str, **kwargs) -> dict[str, Any]:
        folder_map = {
            "presentations": settings.PRESENTATIONS_DIR,
            "generated": settings.GENERATED_DIR,
            "documents": settings.DOCUMENTS_DIR,
            "uploads": settings.UPLOADS_DIR,
            "data": settings.DATA_DIR
        }

        target_dir = folder_map.get(folder_name.lower().strip())
        if not target_dir:
            target_dir = (settings.PROJECT_ROOT / folder_name).resolve()

        if not target_dir.exists():
            return {
                "success": False,
                "action": "open_folder",
                "target": folder_name,
                "message": f"Folder '{folder_name}' does not exist."
            }

        try:
            subprocess.Popen(["explorer.exe", str(target_dir)])
            return {
                "success": True,
                "action": "open_folder",
                "target": str(target_dir),
                "message": f"Opened folder '{target_dir.name}' in Windows File Explorer."
            }
        except Exception as e:
            return {
                "success": False,
                "action": "open_folder",
                "target": str(target_dir),
                "message": f"Failed to open folder: {str(e)}"
            }
