import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union, List

from app.config import settings

def run_virtual_tryon(
    model_path: str,
    clothing_path: str,
    category: int = 0,  # 0=upper, 1=lower, 2=dress
    sample_count: int = 1,
    scale: float = 2.0,
    output_dir: Optional[str] = None
) -> str:
    """
    Run OOTDiffusion for virtual try-on
    
    Args:
        model_path: Path to the model image
        clothing_path: Path to the clothing image
        category: Garment category (0=upper, 1=lower, 2=dress)
        sample_count: Number of samples to generate
        scale: Scale factor for the generation
        output_dir: Directory to save the output
        
    Returns:
        Path to the generated virtual try-on image
    """
    # Ensure category is valid
    if category not in [0, 1, 2]:
        raise ValueError("Category must be 0 (upper), 1 (lower), or 2 (dress)")
    
    # Set the output directory if not provided
    if output_dir is None:
        output_dir = os.path.join(settings.OUTPUT_DIR, "virtual_tryon")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up the command
    cmd = [
        f"source {settings.OOTD_ENV_PATH}/bin/activate",
        "&&",
        "cd", settings.OOTD_DIR,
        "&&",
        "python", f"{settings.OOTD_RUN_SCRIPT}",
        f"--model_path \"{model_path}\"",
        f"--cloth_path \"{clothing_path}\"",
        f"--model_type dc",
        f"--category {category}",
        f"--scale {scale}",
        f"--sample {sample_count}",
        f"--result_dir \"{output_dir}\""
    ]
    
    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(" ".join(cmd), shell=True, check=True)
    
    # Find the generated image
    result_files = list(Path(output_dir).glob("*.png"))
    
    if not result_files:
        raise FileNotFoundError(f"No output images found in {output_dir}")
    
    # Sort by modification time to get the most recent one
    result_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    result_path = str(result_files[0])
    
    # Copy the result to a standard filename
    standard_result_path = os.path.join(output_dir, "result.png")
    subprocess.run(f"cp \"{result_path}\" \"{standard_result_path}\"", shell=True, check=True)
    
    return standard_result_path
