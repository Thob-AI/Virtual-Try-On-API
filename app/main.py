from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import socket
import os
from pathlib import Path
import logging

from app.config import settings
from app.api.routes import router as api_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Virtual Try-On API",
    description="API for generating clothing images and virtual try-on",
    version="1.0.0",
    docs_url="/api/docs",
    servers=[{"url": "http://0.0.0.0:8000", "description": "Local"}],
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

@app.on_event("startup")
async def startup_event():
    """Critical startup initialization"""
    try:
        # Create required directories
        Path(settings.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.STATIC_DIR).mkdir(parents=True, exist_ok=True)

        # Verify default model exists
        default_model = Path(settings.DEFAULT_MODEL_PATH)
        if not default_model.exists():
            logger.error(f"Missing default model at {default_model}")
            raise RuntimeError("Default model image not found")

        # Handle port conflicts
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("0.0.0.0", settings.API_PORT))
        except OSError as e:
            logger.error(f"Port {settings.API_PORT} in use: {e}")
            raise
        finally:
            sock.close()

        logger.info("Startup checks completed successfully")

    except Exception as e:
        logger.critical(f"Startup failed: {str(e)}")
        raise

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def serve_frontend(request: Request):
    """Serve the main interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}