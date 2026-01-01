import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Nepal ID Verifier"
    API_V1_STR: str = "/api/v1"
    MODE: str = "dev"
    
    # Database
    DATABASE_URL: str
    
    # ML
    YOLO_MODEL_PATH: str
    USE_GPU: bool = False
    
    # Flags
    KMP_DUPLICATE_LIB_OK: str = "TRUE"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# --- FORCE CPU IF NEEDED ---
if not settings.USE_GPU:
    os.environ["CUDA_VISIBLE_DEVICES"] = "" # Hides GPU from Paddle/YOLO
    os.environ["PCR_OP_USE_MKLDNN"] = "0"   # Disable MKLDNN explicitly if needed

if settings.KMP_DUPLICATE_LIB_OK == "TRUE":
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"