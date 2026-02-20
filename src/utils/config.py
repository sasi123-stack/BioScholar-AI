"""Configuration management utilities."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = Field(default="biomedical-search-engine", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_workers: int = Field(default=4, alias="API_WORKERS")
    
    # Elasticsearch
    # Elasticsearch
    elasticsearch_host: str = Field(
        default=os.environ.get("ELASTICSEARCH_HOST", "assertive-mahogany-1m2hcasg.us-east-1.bonsaisearch.net"), 
        alias="ELASTICSEARCH_HOST"
    )
    elasticsearch_port: int = Field(default=443, alias="ELASTICSEARCH_PORT")
    elasticsearch_user: str = Field(
        default=os.environ.get("ELASTICSEARCH_USER") or os.environ.get("ELASTICSEARCH_USERNAME") or "0204784e62",
        alias="ELASTICSEARCH_USER"
    )
    elasticsearch_password: str = Field(
        default=os.environ.get("ELASTICSEARCH_PASSWORD", "38aa998d6c5c2891232c"), 
        alias="ELASTICSEARCH_PASSWORD"
    )
    
    # Redis
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    
    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/biomedical_search",
        alias="DATABASE_URL"
    )
    
    # Models
    model_biobert: str = Field(default="dmis-lab/biobert-v1.1", alias="MODEL_BIOBERT")
    model_clinicalbert: str = Field(
        default="emilyalsentzer/Bio_ClinicalBERT",
        alias="MODEL_CLINICALBERT"
    )
    model_qa: str = Field(
        default="dmis-lab/biobert-base-cased-v1.1-squad",
        alias="MODEL_QA"
    )
    model_cache_dir: str = Field(default="./models", alias="MODEL_CACHE_DIR")
    
    @property
    def biobert_model(self) -> str:
        """Get BioBERT model name."""
        return self.model_biobert
    
    @property
    def clinicalbert_model(self) -> str:
        """Get ClinicalBERT model name."""
        return self.model_clinicalbert
    
    @property
    def biobert_qa_model(self) -> str:
        """Get BioBERT QA model name."""
        return self.model_qa
    
    # PubMed
    pubmed_api_key: str = Field(default="", alias="PUBMED_API_KEY")
    pubmed_email: str = Field(default="", alias="PUBMED_EMAIL")
    
    # DeepSeek
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    
    # Gemini
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    
    # Groq
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")

    # Serper (Google Search)
    serper_api_key: str = Field(default="", alias="SERPER_API_KEY")

    # OpenClaw / Generic OpenAI-compatible
    openclaw_api_key: str = Field(default="sk-openclaw-placeholder", alias="OPENCLAW_API_KEY")
    openclaw_api_base: str = Field(default="http://localhost:8000/v1", alias="OPENCLAW_API_BASE")

    
    # Security
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env


def load_yaml_config(config_path: str = "configs/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to YAML config file relative to project root
        
    Returns:
        Dictionary containing configuration
    """
    config_file = PROJECT_ROOT / config_path
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    return config


# Global settings instance
settings = Settings()

# Load YAML config
try:
    yaml_config = load_yaml_config()
except FileNotFoundError:
    yaml_config = {}
