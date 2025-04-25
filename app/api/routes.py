from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import os
import uuid
from pathlib import Path
import subprocess
import time
import shutil
from typing import Optional

from app.config import settings
from app.core.clothing_generator import generate_clothing_image
from app.core.virtual_tryon import run_virtual_tryon
from app.utils.image_utils import is_valid_image

router = APIRouter()

@router.post("/generate-clothing")
async def api_generate_clothing(
    prompt: str = Form(...),
    lora_path: Optional[str] = Form(None),
    lora_scale: float = Form(0.7),
    negative_prompt: Optional[str] = Form(None),
    steps: int = Form(30),
    guidance: float = Form(7.5),
    seed: int = Form(42),
):
    """Generate clothing image using Stable Diffusion 2.1 with LoRA"""
    try:
        # Create a unique ID for this request
        request_id = str(uuid.uuid4())
        output_dir = os.path.join(settings.OUTPUT_DIR, request_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate clothing image
        if lora_path and not lora_path.startswith('/'):
            # If lora_path is just a filename, look in the LORA_DIR
            complete_lora_path = os.path.join(settings.LORA_DIR, lora_path)
            if not os.path.exists(complete_lora_path):
                return JSONResponse(
                    status_code=404,
                    content={"error": f"LoRA file not found: {lora_path}"}
                )
            lora_path = complete_lora_path
            
        image_path = os.path.join(output_dir, "clothing.png")
        
        # Generate the clothing image
        output_path = generate_clothing_image(
            prompt=prompt,
            lora_path=lora_path,
            lora_scale=lora_scale,
            negative_prompt=negative_prompt,
            num_steps=steps,
            guidance_scale=guidance,
            seed=seed,
            output_path=image_path
        )
        
        # Return the image path and URL
        result = {
            "request_id": request_id,
            "image_path": output_path,
            "image_url": f"/api/images/{request_id}/clothing.png"
        }
        
        return result
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generating clothing image: {str(e)}"}
        )

@router.post("/virtual-tryon")
async def api_virtual_tryon(
    clothing_image: Optional[UploadFile] = File(None),
    model_image: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
    lora_path: Optional[str] = Form(None),
    category: int = Form(0),  # 0=upper, 1=lower, 2=dress
    sample_count: int = Form(4),
    scale: float = Form(2.0),
):
    """Run virtual try-on with either uploaded clothing image or generate one from prompt"""
    try:
        # Create a unique ID for this request
        request_id = str(uuid.uuid4())
        output_dir = os.path.join(settings.OUTPUT_DIR, request_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the model image
        model_path = os.path.join(output_dir, "model.png")
        with open(model_path, "wb") as buffer:
            buffer.write(await model_image.read())
        
        # Determine the clothing path
        if clothing_image:
            # Use uploaded clothing image
            clothing_path = os.path.join(output_dir, "clothing.png")
            with open(clothing_path, "wb") as buffer:
                buffer.write(await clothing_image.read())
        elif prompt:
            # Generate clothing from prompt
            if lora_path and not lora_path.startswith('/'):
                # If lora_path is just a filename, look in the LORA_DIR
                complete_lora_path = os.path.join(settings.LORA_DIR, lora_path)
                if not os.path.exists(complete_lora_path):
                    return JSONResponse(
                        status_code=404,
                        content={"error": f"LoRA file not found: {lora_path}"}
                    )
                lora_path = complete_lora_path
            
            clothing_path = os.path.join(output_dir, "clothing.png")
            generate_clothing_image(
                prompt=prompt,
                lora_path=lora_path,
                output_path=clothing_path
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Either clothing_image or prompt must be provided"}
            )
        
        # Run virtual try-on
        result_path = run_virtual_tryon(
            model_path=model_path,
            clothing_path=clothing_path,
            category=category,
            sample_count=sample_count,
            scale=scale,
            output_dir=output_dir
        )
        
        # Return the result
        result = {
            "request_id": request_id,
            "result_path": result_path,
            "result_url": f"/api/images/{request_id}/result.png",
            "model_url": f"/api/images/{request_id}/model.png",
            "clothing_url": f"/api/images/{request_id}/clothing.png"
        }
        
        return result
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error running virtual try-on: {str(e)}"}
        )

@router.get("/images/{request_id}/{filename}")
async def get_image(request_id: str, filename: str):
    """Retrieve a generated image by ID and filename"""
    image_path = os.path.join(settings.OUTPUT_DIR, request_id, filename)
    
    if not os.path.exists(image_path):
        return JSONResponse(
            status_code=404,
            content={"error": f"Image not found: {filename} for request ID {request_id}"}
        )
    
    return FileResponse(image_path)

# Add this endpoint to your routes.py file

@router.get("/available-loras")
async def list_available_loras():
    """List all available LoRA models in the lora directory"""
    try:
        lora_files = []
        for file in os.listdir(settings.LORA_DIR):
            if file.endswith(('.pt', '.safetensors', '.ckpt')):
                lora_files.append({
                    "name": os.path.splitext(file)[0],
                    "path": file
                })
        return lora_files
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error listing LoRA models: {str(e)}"}
        )

# Update the virtual try-on endpoint to handle clothing_url
@router.post("/virtual-tryon")
async def api_virtual_tryon(
    model_image: UploadFile = File(...),
    clothing_image: Optional[UploadFile] = File(None),
    clothing_url: Optional[str] = Form(None),
    prompt: Optional[str] = Form(None),
    lora_path: Optional[str] = Form(None),
    category: int = Form(0),  # 0=upper, 1=lower, 2=dress
    sample_count: int = Form(4),
    scale: float = Form(2.0),
):
    """Run virtual try-on with either uploaded clothing image, URL of previously generated clothing, or generate one from prompt"""
    try:
        # Create a unique ID for this request
        request_id = str(uuid.uuid4())
        output_dir = os.path.join(settings.OUTPUT_DIR, request_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the model image
        model_path = os.path.join(output_dir, "model.png")
        with open(model_path, "wb") as buffer:
            buffer.write(await model_image.read())
        
        # Determine the clothing path
        if clothing_image:
            # Use uploaded clothing image
            clothing_path = os.path.join(output_dir, "clothing.png")
            with open(clothing_path, "wb") as buffer:
                buffer.write(await clothing_image.read())
        elif clothing_url:
            # Extract the request_id and filename from the URL
            # Format is "/api/images/{request_id}/{filename}"
            parts = clothing_url.strip('/').split('/')
            if len(parts) >= 3:
                source_request_id = parts[-2]
                source_filename = parts[-1]
                source_path = os.path.join(settings.OUTPUT_DIR, source_request_id, source_filename)
                
                if os.path.exists(source_path):
                    clothing_path = os.path.join(output_dir, "clothing.png")
                    shutil.copyfile(source_path, clothing_path)
                else:
                    return JSONResponse(
                        status_code=404,
                        content={"error": f"Clothing image not found at URL: {clothing_url}"}
                    )
            else:
                return JSONResponse(
                    status_code=400,
                    content={"error": f"Invalid clothing URL format: {clothing_url}"}
                )
        elif prompt:
            # Generate clothing from prompt
            if lora_path and not lora_path.startswith('/'):
                # If lora_path is just a filename, look in the LORA_DIR
                complete_lora_path = os.path.join(settings.LORA_DIR, lora_path)
                if not os.path.exists(complete_lora_path):
                    return JSONResponse(
                        status_code=404,
                        content={"error": f"LoRA file not found: {lora_path}"}
                    )
                lora_path = complete_lora_path
            
            clothing_path = os.path.join(output_dir, "clothing.png")
            generate_clothing_image(
                prompt=prompt,
                lora_path=lora_path,
                output_path=clothing_path
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "Either clothing_image, clothing_url, or prompt must be provided"}
            )
        
        # Run virtual try-on
        result_path = run_virtual_tryon(
            model_path=model_path,
            clothing_path=clothing_path,
            category=category,
            sample_count=sample_count,
            scale=scale,
            output_dir=output_dir
        )
        
        # Return the result
        result = {
            "request_id": request_id,
            "result_path": result_path,
            "result_url": f"/api/images/{request_id}/result.png",
            "model_url": f"/api/images/{request_id}/model.png",
            "clothing_url": f"/api/images/{request_id}/clothing.png"
        }
        
        return result
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Error running virtual try-on: {str(e)}"}
        )