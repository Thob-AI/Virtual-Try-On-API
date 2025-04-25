from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from pathlib import Path
import subprocess

from app.config import settings
from app.api.routes import router as api_router

# Create the output directory if it doesn't exist
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.STATIC_DIR, exist_ok=True)

app = FastAPI(
    title="Virtual Try-On API",
    description="API for generating clothing images and virtual try-on using SD 2.1 and OOTDiffusion",
    version="1.0.0",
)

# Mount static files directory
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# Set up templates
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}