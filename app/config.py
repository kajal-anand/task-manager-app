import os
from dotenv import load_dotenv
from typing import Optional
import logging
from logging.handlers import RotatingFileHandler

load_dotenv()

class Config:
    """Application configuration class."""
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///tasks.db")
    # OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    SSL_VERIFY: bool = os.getenv("SSL_VERIFY", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def setup_logging():
        """Configure logging with rotating file handler."""
        logger = logging.getLogger()
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        handler = RotatingFileHandler(
            "app.log", maxBytes=1000000, backupCount=5
        )
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)