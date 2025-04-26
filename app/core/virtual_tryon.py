import os
import subprocess
import logging
from pathlib import Path
from typing import Optional

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

def run_virtual_tryon(
    model_path: str,
    clothing_path: str,
    category: int = 0,
    sample_count: int = 1,
    scale: float = 2.0,
) -> str:
    """Run virtual try-on with extensive debugging and error handling"""
    # Validate inputs
    if category not in [0, 1, 2]:
        raise ValueError("Category must be 0 (upper), 1 (lower), or 2 (dress)")
    
    # Validate file existence
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model image not found: {model_path}")
    
    if not os.path.exists(clothing_path):
        raise FileNotFoundError(f"Clothing image not found: {clothing_path}")

    # Set default output directory
    output_dir = output_dir or os.path.join(settings.OUTPUT_DIR, "virtual_tryon")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Environmental debug information
    current_dir = os.getcwd()
    logger.info(f"Current working directory: {current_dir}")
    logger.info(f"OOTD directory: {settings.OOTD_DIR}")
    logger.info(f"Environment path: {settings.OOTD_ENV_PATH}")
    
    # Check for critical directories
    checkpoints_dir = os.path.join(settings.OOTD_DIR, "checkpoints")
    ootd_checkpoints = os.path.join(checkpoints_dir, "ootd")
    
    if not os.path.exists(checkpoints_dir):
        logger.error(f"OOTDiffusion checkpoints directory not found: {checkpoints_dir}")
        raise FileNotFoundError(f"OOTDiffusion checkpoints directory not found: {checkpoints_dir}")
        
    if not os.path.exists(ootd_checkpoints):
        logger.error(f"OOTD model checkpoints not found: {ootd_checkpoints}")
        raise FileNotFoundError(f"OOTD model checkpoints not found: {ootd_checkpoints}")
    
    # Check if run script exists
    run_script = os.path.join(settings.OOTD_DIR, "run", "run_ootd.py")
    if not os.path.exists(run_script):
        logger.error(f"OOTDiffusion run script not found: {run_script}")
        raise FileNotFoundError(f"OOTDiffusion run script not found: {run_script}")
    
    # Create a symbolic link to checkpoints if needed
    root_checkpoints = os.path.join(current_dir, "checkpoints")
    if not os.path.exists(root_checkpoints):
        try:
            # Create symlink to resolve "../checkpoints/ootd" reference
            os.symlink(checkpoints_dir, root_checkpoints)
            logger.info(f"Created symbolic link: {root_checkpoints} -> {checkpoints_dir}")
        except Exception as e:
            logger.warning(f"Could not create symbolic link: {str(e)}")
    
    # Build the execution command
    cmd = [
        f"source {settings.OOTD_ENV_PATH}/bin/activate",
        "&&",
        "cd", settings.OOTD_DIR,
        "&&",
        "python", "run/run_ootd.py",
        f"--model_path \"{model_path}\"",
        f"--cloth_path \"{clothing_path}\"",
        f"--model_type dc",
        f"--category {category}",
        f"--scale {scale}",
        f"--sample {sample_count}",
    ]

    cmd_str = " ".join(cmd)
    logger.info(f"Executing: {cmd_str}")

    # Execute in subshell to maintain environment
    try:
        result = subprocess.run(
            cmd_str, 
            shell=True, 
            executable="/bin/bash", 
            capture_output=True, 
            text=True,
            check=False  # Don't raise exception on non-zero return code
        )
        
        if result.returncode != 0:
            logger.error(f"OOTD failed: {result.stderr}")
            raise RuntimeError(f"OOTDiffusion command failed with return code {result.returncode}: {result.stderr}")
        else:
            logger.info(f"OOTD command succeeded")
            logger.debug(f"OOTD output: {result.stdout}")
            
    except Exception as e:
        logger.error(f"Error running OOTDiffusion: {str(e)}", exc_info=True)
        raise RuntimeError(f"Error executing OOTDiffusion: {str(e)}")

    # Find and return the result
    result_files = list(Path(output_dir).glob("*.png"))
    if not result_files:
        logger.error(f"No output images found in directory: {output_dir}")
        raise FileNotFoundError(f"No output images in {output_dir}")
    
    # Return most recent result
    result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    result_path = result_files[0]
    logger.info(f"Virtual try-on result: {result_path}")
    return str(result_path)