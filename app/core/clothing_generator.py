import os
import torch
from diffusers import StableDiffusionPipeline
from pathlib import Path
from typing import Optional
from safetensors.torch import load_file

from app.config import settings

def generate_clothing_image(
    prompt: str,
    output_path: str,
    lora_path: Optional[str] = None,
    lora_scale: float = 0.7,
    negative_prompt: Optional[str] = None,
    num_steps: int = 30,
    guidance_scale: float = 7.5,
    seed: int = 42
) -> str:
    """Simplified version matching the notebook implementation"""
    # Set default negative prompt
    if not negative_prompt:
        negative_prompt = "wrinkled, dirty, worn, text, logo, brand name, person, model, mannequin, low quality, worst quality, blurry"

    # Initialize pipeline with SD 2.1
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-1-base",
        torch_dtype=torch.float16,
    ).to("cuda")

    # Load LoRA weights if provided
    if lora_path:
        pipe.unet.load_attn_procs(lora_path)

    # Enable memory optimizations
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except:
        print("xformers not available, using default attention")

    # Generate enhanced prompt
    enhanced_prompt = f"{prompt}, on plain white background"
    
    # Create output directory
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate image
    image = pipe(
        prompt=enhanced_prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=num_steps,
        guidance_scale=guidance_scale,
        generator=torch.Generator(device="cuda").manual_seed(seed)
    ).images[0]

    # Save image
    image.save(output_path)
    print(f"Image saved to {output_path}")
    
    return output_path