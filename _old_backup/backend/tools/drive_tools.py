import os
import shutil
import psutil
from pathlib import Path
from typing import Any, Optional
from backend.tools.base import BaseTool
from backend.permissions.models import RiskLevel
from backend.config.settings import settings

class SearchFilesTool(BaseTool):
    name = "search_files"
    description = "Search for files and documents on the computer across Desktop, Documents, Downloads, or Cloud Drive folders by name or extension."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "File name, topic, or extension to search for (e.g. 'syllabus', 'assignment', '.pdf', '.pptx')"
            },
            "location": {
                "type": "string",
                "description": "Folder location to search: 'desktop', 'documents', 'downloads', 'workspace', or 'all'",
                "default": "all"
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str, location: str = "all", **kwargs) -> dict[str, Any]:
        user_home = Path.home()
        search_dirs = []

        loc = location.lower()
        if loc == "desktop":
            search_dirs.append(user_home / "Desktop")
        elif loc == "documents":
            search_dirs.append(user_home / "Documents")
        elif loc == "downloads":
            search_dirs.append(user_home / "Downloads")
        elif loc == "workspace":
            search_dirs.append(Path(settings.BASE_DIR))
        else:
            # Check local common dirs + OneDrive / Google Drive if available
            search_dirs.extend([
                user_home / "Desktop",
                user_home / "Documents",
                user_home / "Downloads",
                Path(settings.BASE_DIR)
            ])
            # Check for Google Drive or OneDrive sync directories
            one_drive = user_home / "OneDrive"
            if one_drive.exists():
                search_dirs.append(one_drive)
            gdrive = user_home / "Google Drive"
            if gdrive.exists():
                search_dirs.append(gdrive)

        results = []
        q_lower = query.lower()

        for s_dir in search_dirs:
            if not s_dir.exists():
                continue
            try:
                for root, _, files in os.walk(str(s_dir)):
                    for f in files:
                        if q_lower in f.lower():
                            full_path = Path(root) / f
                            results.append({
                                "name": f,
                                "path": str(full_path),
                                "size_bytes": full_path.stat().st_size if full_path.exists() else 0,
                                "extension": full_path.suffix.lower()
                            })
                            if len(results) >= 20:
                                break
                    if len(results) >= 20:
                        break
            except Exception:
                continue

        return {
            "success": True,
            "query": query,
            "count": len(results),
            "files": results,
            "message": f"Found {len(results)} matching file(s) for '{query}'."
        }

class ReadFileContentTool(BaseTool):
    name = "read_file_content"
    description = "Read the text contents of a document or file from the computer."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Full path to the file to read"
            }
        },
        "required": ["file_path"]
    }

    def execute(self, file_path: str, **kwargs) -> dict[str, Any]:
        p = Path(file_path)
        if not p.exists():
            return {
                "success": False,
                "error": f"File does not exist: {file_path}"
            }

        ext = p.suffix.lower()
        content = ""
        try:
            if ext in [".txt", ".md", ".py", ".json", ".csv", ".log"]:
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(4000)
            elif ext == ".pdf":
                import pypdf
                reader = pypdf.PdfReader(str(p))
                for page in reader.pages[:5]:
                    content += page.extract_text() or ""
            elif ext == ".docx":
                import docx
                doc = docx.Document(str(p))
                content = "\n".join([para.text for para in doc.paragraphs[:40]])
            else:
                return {
                    "success": False,
                    "error": f"Unsupported file type for preview: {ext}"
                }

            return {
                "success": True,
                "file_name": p.name,
                "file_path": str(p),
                "preview": content[:2000],
                "length": len(content)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error reading file {p.name}: {str(e)}"
            }

class OpenDriveFolderTool(BaseTool):
    name = "open_drive_folder"
    description = "Open Google Drive, OneDrive, Downloads, Desktop, or a project folder in Windows Explorer."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {
            "folder_name": {
                "type": "string",
                "description": "Target folder: 'drive', 'onedrive', 'desktop', 'documents', 'downloads', or 'workspace'",
                "default": "workspace"
            }
        }
    }

    def execute(self, folder_name: str = "workspace", **kwargs) -> dict[str, Any]:
        user_home = Path.home()
        target = Path(settings.BASE_DIR)

        fn = folder_name.lower()
        if "drive" in fn or "gdrive" in fn:
            candidates = [
                user_home / "Google Drive",
                Path("G:\\"),
                user_home / "OneDrive"
            ]
            for c in candidates:
                if c.exists():
                    target = c
                    break
        elif "onedrive" in fn:
            od = user_home / "OneDrive"
            if od.exists():
                target = od
        elif "desktop" in fn:
            target = user_home / "Desktop"
        elif "download" in fn:
            target = user_home / "Downloads"
        elif "document" in fn:
            target = user_home / "Documents"

        import subprocess
        subprocess.Popen(["explorer.exe", str(target.resolve())])
        return {
            "success": True,
            "action": "open_folder",
            "folder": str(target),
            "message": f"Opened folder '{target.name}' in File Explorer."
        }

class GetSystemTelemetryTool(BaseTool):
    name = "get_system_telemetry"
    description = "Retrieve real-time computer telemetry including CPU utilization percentage, RAM percentage, disk space, and battery status."
    risk_level = RiskLevel.LOW_RISK
    parameters = {
        "type": "object",
        "properties": {}
    }

    def execute(self, **kwargs) -> dict[str, Any]:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent
        battery = None
        if hasattr(psutil, "sensors_battery"):
            b = psutil.sensors_battery()
            if b:
                battery = {"percent": b.percent, "power_plugged": b.power_plugged}

        return {
            "success": True,
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk,
            "battery": battery,
            "status": "OPERATIONAL",
            "message": f"System Telemetry: CPU {cpu}%, RAM {ram}%, Disk {disk}%."
        }
