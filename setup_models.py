#!/usr/bin/env python3
import os
import subprocess
import argparse
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and print output"""
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, check=True, cwd=cwd)
    print(f"Command completed with return code: {process.returncode}")
    return process.returncode

def setup_environments(base_dir):
    """Set up virtual environments for SD and OOTDiffusion"""
    # Create directories
    os.makedirs(f"{base_dir}/models/lora", exist_ok=True)
    os.makedirs(f"{base_dir}/models/ootd", exist_ok=True)
    
    print("\n=== Setting up virtual environments ===\n")
    
    # Install virtualenv if not available
    run_command("pip install virtualenv -q")
    
    # Create SD environment
    run_command(f"virtualenv {base_dir}/envs/sd_env")
    
    # Install PyTorch and SD requirements
    run_command(f". {base_dir}/envs/sd_env/bin/activate && pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118 -q")
    run_command(f". {base_dir}/envs/sd_env/bin/activate && pip install -r {base_dir}/requirements_sdxl.txt -q")
    run_command(f". {base_dir}/envs/sd_env/bin/activate && pip install fastapi uvicorn python-multipart -q")
    
    # Create OOTDiffusion environment
    run_command(f"virtualenv {base_dir}/envs/ootd_env")
    
    # Install PyTorch and OOTDiffusion requirements
    run_command(f". {base_dir}/envs/ootd_env/bin/activate && pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 --index-url https://download.pytorch.org/whl/cu118 -q")
    run_command(f". {base_dir}/envs/ootd_env/bin/activate && pip install -r {base_dir}/requirements_ootd.txt -q")
    
    print("\nVirtual environments created successfully")

def clone_ootdiffusion(base_dir):
    """Clone OOTDiffusion repository and download required checkpoints"""
    print("\n=== Cloning OOTDiffusion and downloading checkpoints ===\n")
    
    # Clone OOTDiffusion
    run_command("git lfs install")
    run_command(f"git clone https://github.com/levihsu/OOTDiffusion {base_dir}/OOTDiffusion")
    
    # Change directory to OOTDiffusion
    ootd_dir = f"{base_dir}/OOTDiffusion"
    
    # Clone checkpoints
    run_command(f"git clone https://huggingface.co/openai/clip-vit-large-patch14 {ootd_dir}/checkpoints/clip-vit-large-patch14", cwd=ootd_dir)
    run_command(f"git clone https://huggingface.co/levihsu/OOTDiffusion {ootd_dir}/OOTDiffusion", cwd=ootd_dir)
    
    # Move checkpoints to proper locations
    run_command(f"mv -n {ootd_dir}/OOTDiffusion/checkpoints/ootd {ootd_dir}/checkpoints", cwd=ootd_dir)
    run_command(f"mv -n {ootd_dir}/OOTDiffusion/checkpoints/humanparsing {ootd_dir}/checkpoints", cwd=ootd_dir)
    run_command(f"mv -n {ootd_dir}/OOTDiffusion/checkpoints/openpose {ootd_dir}/checkpoints", cwd=ootd_dir)
    
    print("\nOOTDiffusion and checkpoints cloned successfully")
    
    # Fix potential issues with diffusers import
    ootd_env = f"{base_dir}/envs/ootd_env"
    diffusers_path = f"{ootd_env}/lib/python3.*/site-packages/diffusers/utils/dynamic_modules_utils.py"
    
    print("\n=== Fixing diffusers import issue ===\n")
    # Find all matching files and fix them (could be different Python versions)
    for file_path in Path(base_dir).glob(diffusers_path.replace(base_dir, "")):
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
            
            # Fix import
            content = content.replace(
                "from huggingface_hub import HfFolder, cached_download, hf_hub_download, model_info",
                "from huggingface_hub import HfFolder, hf_hub_download, model_info"
            )
            
            with open(full_path, 'w') as f:
                f.write(content)
            
            print(f"Fixed import in {full_path}")

def main():
    parser = argparse.ArgumentParser(description="Set up environments and models for virtual try-on API")
    parser.add_argument("--base-dir", type=str, default=".", help="Base directory for the project")
    
    args = parser.parse_args()
    base_dir = os.path.abspath(args.base_dir)
    
    print(f"Setting up project in {base_dir}")
    
    # Create base directories
    os.makedirs(f"{base_dir}/envs", exist_ok=True)
    
    # Setup environments
    setup_environments(base_dir)
    
    # Clone OOTDiffusion and download checkpoints
    clone_ootdiffusion(base_dir)
    
    print("\n=== Setup complete! ===")
    print(f"Project setup in {base_dir}")
    print("Next steps:")
    print("1. Update the configuration in app/config.py if needed")
    print("2. Run the FastAPI application with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()