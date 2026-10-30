import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config.settings import settings
from backend.database.seed import init_db
from backend.reminders.scheduler import reminder_scheduler

# Import Routers
from backend.api.routes_chat import router as chat_router
from backend.api.routes_permissions import router as permissions_router
from backend.api.routes_lms import router as lms_router
from backend.api.routes_email import router as email_router
from backend.api.routes_calendar import router as calendar_router
from backend.api.routes_reminders import router as reminders_router
from backend.api.routes_documents import router as documents_router
from backend.api.routes_presentations import router as presentations_router
from backend.api.routes_voice import router as voice_router
from backend.api.routes_activity import router as activity_router
from backend.api.routes_system import router as system_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("jarvis")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing JARVIS Database & Services...")
    init_db()
    reminder_scheduler.start()
    yield
    reminder_scheduler.stop()
    logger.info("JARVIS Services gracefully stopped.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Permission-Aware Autonomous AI Agent for Student Productivity & Windows Automation",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for generated files (presentations, audio, etc.)
app.mount("/generated", StaticFiles(directory=str(settings.GENERATED_DIR)), name="generated")
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")

# Include Routers
app.include_router(chat_router)
app.include_router(permissions_router)
app.include_router(lms_router)
app.include_router(email_router)
app.include_router(calendar_router)
app.include_router(reminders_router)
app.include_router(documents_router)
app.include_router(presentations_router)
app.include_router(voice_router)
app.include_router(activity_router)
app.include_router(system_router)

from pathlib import Path
from fastapi.responses import FileResponse

# Check if frontend/dist exists to serve UI directly from FastAPI
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if (frontend_dist / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="frontend_assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Exclude API endpoints, Swagger, and static storage mounts
        api_prefixes = (
            "docs", "openapi.json", "chat", "permissions", "courses", 
            "assignments", "exams", "announcements", "emails", "calendar", 
            "reminders", "documents", "presentations", "voice", "activity", 
            "health", "system", "generated", "uploads"
        )
        if any(full_path == p or full_path.startswith(f"{p}/") for p in api_prefixes):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API route not found")
        
        target_file = frontend_dist / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "demo_mode": settings.DEMO_MODE,
            "status": "online",
            "docs_url": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
