"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Smart Grid IoT Analytics"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql://smartgrid_user:smartgrid_pass@localhost:5432/smartgrid"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # MQTT
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    MQTT_KEEPALIVE: int = 60
    
    # API Keys
    OPENWEATHER_API_KEY: Optional[str] = None
    SOLAR_FORECAST_API_KEY: Optional[str] = None
    
    # JWT
    JWT_SECRET_KEY: str = "your_super_secret_jwt_key_here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # ML Configuration
    MODEL_UPDATE_INTERVAL_HOURS: int = 24
    LSTM_SEQUENCE_LENGTH: int = 168  # 7 days of hourly data
    PREDICTION_HORIZON_HOURS: int = 24
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Smart Meter Configuration
    METER_DATA_RETENTION_DAYS: int = 365
    METER_READING_INTERVAL_MINUTES: int = 15
    
    # Energy Pricing
    BASE_ENERGY_PRICE: float = 0.12  # $/kWh
    PEAK_HOUR_MULTIPLIER: float = 1.5
    OFF_PEAK_MULTIPLIER: float = 0.8
    
    # Weather API
    WEATHER_UPDATE_INTERVAL_MINUTES: int = 30
    WEATHER_FORECAST_DAYS: int = 7
    
    # Renewable Energy
    SOLAR_PANEL_EFFICIENCY: float = 0.20
    WIND_TURBINE_EFFICIENCY: float = 0.35
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
