"""Configuration management for Super-Scraper"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    app_name: str = os.getenv("APP_NAME", "Super-Scraper")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # AI Models
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Search APIs
    serpapi_key: str = os.getenv("SERPAPI_KEY", "")
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")
    
    # Scraping
    firecrawl_api_key: str = os.getenv("FIRECRAWL_API_KEY", "")
    
    # Database
    database_path: str = os.getenv("DATABASE_PATH", "./data/scraper.db")
    
    # Paths
    data_dir: Path = Path("./data")
    leads_dir: Path = Path("./data/leads")
    cache_dir: Path = Path("./data/cache")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def ensure_directories(self):
        """Create necessary directories"""
        self.data_dir.mkdir(exist_ok=True)
        self.leads_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)

# Global settings instance
settings = Settings()
settings.ensure_directories()

# Configure Google API key as environment variable for google-generativeai
if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key
    # Also configure google.generativeai directly
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
    except ImportError:
        pass  # google-generativeai not installed
