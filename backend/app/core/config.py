"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Decolonial Fact Checker"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Wikipedia API
    WIKIPEDIA_USER_AGENT: str = "DecolonialFactChecker/1.0"
    
    # NLP Models
    SPACY_MODEL_EN: str = "en_core_web_trf"
    SPACY_MODEL_MULTILINGUAL: str = "xx_ent_wiki_sm"
    
    # Analysis Settings
    PASSIVE_VIOLENCE_THRESHOLD: float = 0.3
    COLONIAL_LANGUAGE_SEVERITY_WEIGHTS: dict = {
        "high": 1.0,
        "medium": 0.5,
        "low": 0.2
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
