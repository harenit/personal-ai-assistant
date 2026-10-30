import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field

# Base Directory: root of the project (parent of backend)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # App General
    APP_NAME: str = "JARVIS - Autonomous AI Student Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DEMO_MODE: bool = True
    
    # Network
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # LLM Settings
    LLM_PROVIDER: str = "ollama"  # "ollama", "openai", "mock"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text:latest"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Paths
    PROJECT_ROOT: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    DOCUMENTS_DIR: Path = BASE_DIR / "data" / "documents"
    VECTORSTORE_DIR: Path = BASE_DIR / "data" / "vectorstore"
    UPLOADS_DIR: Path = BASE_DIR / "uploads"
    GENERATED_DIR: Path = BASE_DIR / "generated"
    PRESENTATIONS_DIR: Path = BASE_DIR / "generated" / "presentations"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{(BASE_DIR / 'data' / 'jarvis.db').as_posix()}"
    
    # Voice Settings
    WAKE_WORD_ENABLED: bool = False
    WAKE_WORD: str = "Hey JARVIS"
    STT_PROVIDER: str = "whisper"  # "whisper", "speech_recognition", "web_speech"
    TTS_ENABLED: bool = True
    TTS_VOICE_RATE: int = 175
    
    # Security & Allowlist
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_APP_NAMES: list[str] = [
        "calculator", "calc",
        "notepad",
        "explorer", "file explorer",
        "edge", "microsoft edge",
        "chrome", "google chrome",
        "code", "vscode", "visual studio code",
        "powerpoint", "powerpnt",
        "word", "winword",
        "paint", "mspaint"
    ]

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Ensure runtime directories exist
for folder in [
    settings.DATA_DIR,
    settings.DOCUMENTS_DIR,
    settings.VECTORSTORE_DIR,
    settings.UPLOADS_DIR,
    settings.GENERATED_DIR,
    settings.PRESENTATIONS_DIR,
    settings.LOGS_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)
