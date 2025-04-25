from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import socket

from app.config import settings

app = FastAPI(
    title="Virtual Try-On API",
    description="API for generating clothing images and virtual try-on",
    version="1.0.0",
    servers=[{"url": "http://0.0.0.0:8000", "description": "Local"}]
)

# Setup directories
Path(settings.STATIC_DIR).mkdir(exist_ok=True)
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.OUTPUT_DIR).mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)

@app.on_event("startup")
async def startup_events():
    # Create default favicon
    favicon_path = Path(settings.STATIC_DIR) / "favicon.ico"
    if not favicon_path.exists():
        with open(favicon_path, "wb") as f:
            f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x18\x00h\x03\x00\x00&\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    # Handle port conflicts
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", 8000))
    except OSError:
        print("Port 8000 already in use - reusing connection")
    finally:
        sock.close()

@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    return Response(status_code=204)

# Rest of your routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    return {"status": "ok"}