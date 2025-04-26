import os
import subprocess
import logging
from pathlib import Path
import shutil
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

    # Set up absolute paths to prevent directory issues
    run_dir = os.path.join(settings.OOTD_DIR, "run")
    ootd_output_dir = os.path.join(run_dir, "images_output")
    
    # Ensure output directory exists
    Path(ootd_output_dir).mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensuring output directory exists: {ootd_output_dir}")

    # Environmental debug information
    current_dir = os.getcwd()
    logger.info(f"Current working directory: {current_dir}")
    logger.info(f"OOTD directory: {settings.OOTD_DIR}")
    logger.info(f"Environment path: {settings.OOTD_ENV_PATH}")
    logger.info(f"Output directory for OOTD: {ootd_output_dir}")
    
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
    run_script = os.path.join(run_dir, "run_ootd.py")
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
    
    # Build the execution command with explicit creation of output directory
    cmd = [
        f"source {settings.OOTD_ENV_PATH}/bin/activate",
        "&&",
        f"mkdir -p {ootd_output_dir}",  # Explicitly create directory
        "&&",
        "cd", run_dir,  # Change to run directory, not just OOTDiffusion
        "&&",
        "python", "run_ootd.py",
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
            logger.error(f"OOTD output: {result.stdout}")
            raise RuntimeError(f"OOTDiffusion command failed with return code {result.returncode}: {result.stderr}")
        else:
            logger.info(f"OOTD command succeeded")
            logger.debug(f"OOTD output: {result.stdout}")
            
    except Exception as e:
        logger.error(f"Error running OOTDiffusion: {str(e)}", exc_info=True)
        raise RuntimeError(f"Error executing OOTDiffusion: {str(e)}")

    # Find and return the result
    # Create a unique request ID directory for this result
    request_id = Path(clothing_path).parent.name
    api_output_dir = Path(settings.OUTPUT_DIR) / request_id
    api_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find the output files - check both with absolute and relative paths
    result_files = list(Path(ootd_output_dir).glob("out_*.png"))
    
    if not result_files:
        # Try looking in the working directory structure as well
        alternate_output_dir = os.path.join(current_dir, "OOTDiffusion", "run", "images_output")
        logger.info(f"No output found in {ootd_output_dir}, checking alternate path: {alternate_output_dir}")
        result_files = list(Path(alternate_output_dir).glob("out_*.png"))
    
    if not result_files:
        # Try looking directly in the run directory
        run_output_dir = os.path.join(run_dir, "images_output")
        logger.info(f"Still no output found, checking directory: {run_output_dir}")
        result_files = list(Path(run_output_dir).glob("out_*.png"))
        
    if not result_files:
        # Try a complete search in the OOTD directory
        logger.info(f"Searching entire OOTD directory for output...")
        for root, _, files in os.walk(settings.OOTD_DIR):
            for file in files:
                if file.startswith("out_") and file.endswith(".png"):
                    result_files.append(Path(os.path.join(root, file)))
        
    if not result_files:
        logger.error(f"No output images found in directory or subdirectories")
        raise FileNotFoundError(f"No output images found after running OOTDiffusion")
    
    # Sort by modification time and get most recent
    result_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    source_path = result_files[0]
    logger.info(f"Found result file: {source_path}")
    
    # Copy the file to our API output directory
    dest_path = api_output_dir / f"result_{source_path.name}"
    shutil.copy2(source_path, dest_path)
    
    logger.info(f"Virtual try-on result copied to: {dest_path}")
    return str(dest_path)