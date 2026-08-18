from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GROQ_MODEL_PRIMARY: str = "openai/gpt-oss-120b"
    GROQ_MODEL_FALLBACK: str = "qwen/qwen3.6-27b"
    GROQ_API_BASE: str = "https://api.groq.com/openai/v1"
    
    DATABASE_URL: str
    
    CLOUDINARY_URL: str
    
    CNN_MODEL_PATH: str = "data/models/cnn_archetype.pt"
    HMM_MODELS_DIR: str = "data/models/"
    TRENDS_CACHE_DIR: str = "data/trends_cache/"
    
    MONTE_CARLO_SIMULATIONS: int = 10000
    MONTE_CARLO_SEED: int = 42

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
