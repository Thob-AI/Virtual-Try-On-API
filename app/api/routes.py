from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import uuid
import shutil
from pathlib import Path
from typing import Optional

from app.config import settings
from app.core.clothing_generator import generate_clothing_image
from app.core.virtual_tryon import run_virtual_tryon
from app.utils.image_utils import is_valid_image

router = APIRouter()

# Simplified clothing generation endpoint
@router.post("/generate-clothing")
async def api_generate_clothing(
    prompt: str = Form(...),  # Only required field
    lora_scale: float = Form(0.7),
    steps: int = Form(30),
    guidance: float = Form(7.5),
    seed: int = Form(42)
):
    """Generate clothing image with default parameters"""
    try:
        request_id = str(uuid.uuid4())
        output_dir = Path(settings.OUTPUT_DIR) / request_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate clothing image with defaults
        image_path = output_dir / "clothing.png"
        generate_clothing_image(
            prompt=prompt,
            lora_scale=lora_scale,
            num_steps=steps,
            guidance_scale=guidance,
            seed=seed,
            output_path=str(image_path)
        )

        return {
            "request_id": request_id,
            "clothing_url": f"/api/images/{request_id}/clothing.png"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simplified virtual try-on endpoint
@router.post("/virtual-tryon")
async def api_virtual_tryon(
    clothing_url: str = Form(...),  # Required from previous generation
    category: int = Form(0),       # Default: upper body
    sample_count: int = Form(1),   # Default: 1 sample
    scale: float = Form(2.0)       # Default scale
):
    """Run virtual try-on with default model image"""
    try:
        request_id = str(uuid.uuid4())
        output_dir = Path(settings.OUTPUT_DIR) / request_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Use default model image
        model_path = output_dir / "model.png"
        default_model = Path(settings.DEFAULT_MODEL_PATH)
        if not default_model.exists():
            raise HTTPException(status_code=500, detail="Default model image missing")
        shutil.copyfile(default_model, model_path)

        # Process clothing URL
        path_parts = clothing_url.strip('/').split('/')
        if len(path_parts) < 4 or path_parts[0] != 'api' or path_parts[1] != 'images':
            raise HTTPException(status_code=400, detail="Invalid clothing URL format")

        source_id, filename = path_parts[-2], path_parts[-1]
        source_path = Path(settings.OUTPUT_DIR) / source_id / filename
        
        if not source_path.exists():
            raise HTTPException(status_code=404, detail="Clothing image not found")

        clothing_path = output_dir / "clothing.png"
        shutil.copyfile(source_path, clothing_path)

        # Run virtual try-on
        result_path = run_virtual_tryon(
            model_path=str(model_path),
            clothing_path=str(clothing_path),
            category=category,
            sample_count=sample_count,
            scale=scale,
            output_dir=str(output_dir)
        )

        return {
            "result_url": f"/api/images/{request_id}/result.png"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Image retrieval endpoint remains the same
@router.get("/images/{request_id}/{filename}")
async def get_image(request_id: str, filename: str):
    try:
        image_path = Path(settings.OUTPUT_DIR) / request_id / filename
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="Image not found")
        return FileResponse(image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))