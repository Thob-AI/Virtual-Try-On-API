import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        protected_namespaces=()
    ) 
    
    BASE_DIR: str = str(Path(__file__).parent.parent.resolve())
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    OUTPUT_DIR: str = os.path.join(BASE_DIR, "outputs")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")
    TEMPLATES_DIR: str = os.path.join(BASE_DIR, "templates")
    DEFAULT_MODEL_PATH: str = os.path.join(STATIC_DIR, "images", "default_model.jpg")
    SD_ENV_PATH: str = os.path.join(BASE_DIR, "envs/sd_env")
    OOTD_ENV_PATH: str = os.path.join(BASE_DIR, "envs/ootd_env")
    OOTD_DIR: str = os.path.join(BASE_DIR, "OOTDiffusion")
    OOTD_RUN_SCRIPT: str = os.path.join(OOTD_DIR, "run/run_ootd.py")
    LORA_DIR: str = os.path.join(MODELS_DIR, "lora")
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

settings = Settings()