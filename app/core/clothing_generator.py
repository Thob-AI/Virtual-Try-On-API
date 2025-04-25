import os
import subprocess
import sys
import json
from pathlib import Path
from typing import Optional

from app.config import settings

def generate_clothing_image(
    prompt: str,
    lora_path: Optional[str] = None,
    lora_scale: float = 0.7,
    negative_prompt: Optional[str] = None,
    num_steps: int = 30,
    guidance_scale: float = 7.5,
    seed: int = 42,
    output_path: Optional[str] = None
) -> str:
    """
    Generate clothing image using Stable Diffusion 2.1 with optional LoRA
    
    Args:
        prompt: The text prompt for generating the clothing
        lora_path: Path to the LoRA weights file (optional)
        lora_scale: Scale factor for the LoRA weights
        negative_prompt: Negative prompt to guide generation (optional)
        num_steps: Number of diffusion steps
        guidance_scale: Guidance scale for diffusion
        seed: Random seed for reproducibility
        output_path: Path to save the generated image (optional)
        
    Returns:
        Path to the generated image
    """
    # Create a script to run in the SD environment
    script_content = """
import sys
import os
import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
import json
import argparse

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, required=True)
    parser.add_argument("--lora_path", type=str)
    parser.add_argument("--lora_scale", type=float, default=0.7)
    parser.add_argument("--negative_prompt", type=str)
    parser.add_argument("--num_steps", type=int, default=30)
    parser.add_argument("--guidance_scale", type=float, default=7.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output_path", type=str, required=True)
    
    args = parser.parse_args()
    
    # Set default negative prompt if not provided
    if not args.negative_prompt:
        args.negative_prompt = "wrinkled, dirty, worn, text, logo, brand name, person, model, mannequin, low quality, worst quality, bad anatomy, blurry"
    
    # Initialize pipeline with SD 2.1
    pipe = StableDiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-1-base",
        torch_dtype=torch.float16,
        safety_checker=None
    ).to("cuda")
    
    
    # Load and apply LoRA weights if provided
    if args.lora_path:
        print(f"Loading LoRA from {args.lora_path}")
        pipe.unet.load_attn_procs(lora_path)
    
    # Enable memory optimizations
    try:
        pipe.enable_xformers_memory_efficient_attention()
    except:
        print("xformers not available, using default attention")
    
    
    args.prompt = f"{args.prompt}, on plain white background"
    
    print(f"Generating image with prompt: {args.prompt}")
    image = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        num_inference_steps=args.num_steps,
        guidance_scale=args.guidance_scale,
        generator=generator,
        cross_attention_kwargs={"scale": args.lora_scale} if args.lora_path else None
    ).images[0]
    
    # Save image
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    image.save(args.output_path)
    print(f"Image saved to {args.output_path}")
    
    return args.output_path

if __name__ == "__main__":
    main()
"""
    
    # Create a temporary script file
    script_path = os.path.join(settings.BASE_DIR, "temp_sd_script.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Set the output path if not provided
    if output_path is None:
        output_path = os.path.join(settings.OUTPUT_DIR, f"clothing_{seed}.png")
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create the command
    cmd = [
        f"source {settings.SD_ENV_PATH}/bin/activate",
        "&&",
        "python",
        script_path,
        f"--prompt \"{prompt}\"",
        f"--output_path \"{output_path}\"",
        f"--num_steps {num_steps}",
        f"--guidance_scale {guidance_scale}",
        f"--seed {seed}"
    ]
    
    # Add optional arguments if provided
    if lora_path:
        cmd.append(f"--lora_path \"{lora_path}\"")
        cmd.append(f"--lora_scale {lora_scale}")
    
    if negative_prompt:
        cmd.append(f"--negative_prompt \"{negative_prompt}\"")
    
    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(" ".join(cmd), shell=True, check=True)
    
    # Clean up the temporary script
    os.remove(script_path)
    
    return output_path
