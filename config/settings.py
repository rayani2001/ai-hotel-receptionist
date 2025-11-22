"""
Configuration Settings Module
Centralized configuration management using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application Settings
    APP_NAME: str = "AI Hotel Receptionist"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Hotel Configuration
    HOTEL_NAME: str = Field(default="Grand Plaza Hotel", env="HOTEL_NAME")
    HOTEL_ADDRESS: str = "123 Main Street, City, Country"
    HOTEL_PHONE: str = "+1-234-567-8900"
    HOTEL_EMAIL: str = "info@grandplaza.com"
    
    # AI Provider Configuration
    AI_PROVIDER: str = Field(default="openai", env="AI_PROVIDER")  # "openai" or "anthropic"
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Model Configuration
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    ANTHROPIC_MODEL: str = "claude-sonnet-4"
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="sqlite:///./hotel_receptionist.db",
        env="DATABASE_URL"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Voice Configuration
    ENABLE_VOICE: bool = True
    SPEECH_LANGUAGE: str = "en-IN"
    TTS_PROVIDER: str = "gtts"  # "gtts" or "elevenlabs"
    
    # Language Support
    SUPPORTED_LANGUAGES: list = [
        "en",  # English
        "hi",  # Hindi
        "ta",  # Tamil
        "te",  # Telugu
        "kn",  # Kannada
    ]
    
    # Intent Configuration
    INTENT_CONFIDENCE_THRESHOLD: float = 0.7
    ENTITY_CONFIDENCE_THRESHOLD: float = 0.6
    MAX_CONVERSATION_TURNS: int = 20
    
    # Room Types and Pricing (can be moved to database)
    ROOM_TYPES: dict = {
        "single": {
            "name": "Single Room",
            "price": 1500,
            "capacity": 1,
            "amenities": ["WiFi", "TV", "AC"]
        },
        "double": {
            "name": "Double Room",
            "price": 2500,
            "capacity": 2,
            "amenities": ["WiFi", "TV", "AC", "Mini Bar"]
        },
        "deluxe": {
            "name": "Deluxe Room",
            "price": 3500,
            "capacity": 2,
            "amenities": ["WiFi", "Smart TV", "AC", "Mini Bar", "Balcony"]
        },
        "suite": {
            "name": "Executive Suite",
            "price": 5500,
            "capacity": 4,
            "amenities": ["WiFi", "Smart TV", "AC", "Mini Bar", "Balcony", "Living Room"]
        }
    }
    
    # Dining Options
    DINING_OPTIONS: dict = {
        "breakfast": {
            "name": "Breakfast Buffet",
            "price": 500,
            "timings": "7:00 AM - 10:30 AM"
        },
        "lunch": {
            "name": "Lunch Buffet",
            "price": 800,
            "timings": "12:00 PM - 3:00 PM"
        },
        "dinner": {
            "name": "Dinner Buffet",
            "price": 1000,
            "timings": "7:00 PM - 11:00 PM"
        }
    }
    
    # Party Hall Configuration
    PARTY_HALLS: dict = {
        "small": {
            "name": "Royal Hall",
            "capacity": 50,
            "price_per_hour": 5000
        },
        "medium": {
            "name": "Grand Ballroom",
            "capacity": 150,
            "price_per_hour": 12000
        },
        "large": {
            "name": "Imperial Hall",
            "capacity": 300,
            "price_per_hour": 20000
        }
    }
    
    # Business Hours
    CHECK_IN_TIME: str = "14:00"
    CHECK_OUT_TIME: str = "11:00"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    AUDIO_DIR: Path = BASE_DIR / "audio"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create necessary directories
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)
