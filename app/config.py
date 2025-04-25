import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    BASE_DIR: str = Path(__file__).parent.parent.resolve()
    
    # Project structure
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "outputs")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "templates")
    
    # Default model path (optional)
    DEFAULT_MODEL_PATH: str = os.path.join(STATIC_DIR, "images", "default_model.jpg")
    
    # Environment paths
    SD_ENV_PATH: str = os.path.join(BASE_DIR, "envs/sd_env")
    OOTD_ENV_PATH: str = os.path.join(BASE_DIR, "envs/ootd_env")
    
    # OOTDiffusion paths
    OOTD_DIR: str = os.path.join(BASE_DIR, "OOTDiffusion")
    OOTD_RUN_SCRIPT: str = os.path.join(OOTD_DIR, "run/run_ootd.py")
    
    # LoRA paths
    LORA_DIR: str = os.path.join(MODELS_DIR, "lora")
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
