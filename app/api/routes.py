from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
import shutil
import logging
from pathlib import Path
from typing import Optional

from app.config import settings
from app.core.clothing_generator import generate_clothing_image
from app.core.virtual_tryon import run_virtual_tryon
from app.utils.image_utils import is_valid_image

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

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
        # Auto-append background requirement
        if "plain white background" not in prompt.lower():
            prompt += ", on plain white background"

        request_id = uuid.uuid4().hex
        output_dir = Path(settings.OUTPUT_DIR) / request_id
        output_dir.mkdir(parents=True, exist_ok=True)

        clothing_path = output_dir / "clothing.png"
        
        # Call updated generator
        generate_clothing_image(
            prompt=prompt,
            output_path=str(clothing_path),
            lora_scale=lora_scale,
            num_steps=steps,
            guidance_scale=guidance,
            seed=seed
        )

        return {
            "request_id": request_id,
            "clothing_url": f"/api/images/{request_id}/clothing.png"
        }

    except Exception as e:
        logger.error(f"Clothing generation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Improved virtual try-on endpoint with better error logging
@router.post("/virtual-tryon")
async def api_virtual_tryon(
    clothing_url: str = Form(...),  # From previous generation
    category: int = Form(0)         # Default: upper body
):
    """Run try-on with default parameters"""
    try:
        request_id = uuid.uuid4().hex
        output_dir = Path(settings.OUTPUT_DIR) / request_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Process clothing URL
        path_parts = clothing_url.strip('/').split('/')
        if len(path_parts) < 4 or path_parts[0] != 'api' or path_parts[1] != 'images':
            raise HTTPException(400, "Invalid clothing URL format")

        source_id, filename = path_parts[-2], path_parts[-1]
        source_path = Path(settings.OUTPUT_DIR) / source_id / filename
        
        logger.info(f"Virtual try-on request: clothing={source_path}, category={category}")
        
        if not source_path.exists():
            logger.error(f"Source clothing image not found: {source_path}")
            raise HTTPException(404, "Clothing image not found")
        
        # Run try-on with simplified parameters
        try:
            result_path = run_virtual_tryon(
                model_path=str(Path(settings.DEFAULT_MODEL_PATH)),
                clothing_path=str(source_path),
                category=category,
                sample_count=1,
                scale=2.0
            )
            
            logger.info(f"Virtual try-on completed successfully: {result_path}")
            
            # Get the filename from the result path
            result_filename = Path(result_path).name
            result_id = Path(result_path).parent.name
            
            return {
                "result_url": f"/api/images/{result_id}/{result_filename}"
            }
        except Exception as e:
            logger.error(f"Virtual try-on process failed: {str(e)}", exc_info=True)
            raise HTTPException(500, f"Virtual try-on process failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Virtual try-on endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Updated image retrieval endpoint with better error handling
@router.get("/images/{request_id}/{filename}")
async def get_image(request_id: str, filename: str):
    try:
        image_path = Path(settings.OUTPUT_DIR) / request_id / filename
        logger.info(f"Image request: {image_path}")
        
        if not image_path.exists():
            logger.error(f"Image not found: {image_path}")
            raise HTTPException(status_code=404, detail="Image not found")
            
        return FileResponse(str(image_path))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image retrieval error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))