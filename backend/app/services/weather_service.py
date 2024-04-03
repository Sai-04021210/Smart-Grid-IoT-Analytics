"""
Weather Service for Renewable Energy Forecasting
Integrates with OpenWeatherMap API for weather data
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for fetching and processing weather data"""
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        
    def get_current_weather(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        """Get current weather data for a location"""
        try:
            if not self.api_key:
                logger.warning("OpenWeatherMap API key not configured")
                return None
            
            url = f"{self.base_url}/weather"
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "timestamp": datetime.utcnow(),
                "temperature_c": data["main"]["temp"],
                "humidity_percent": data["main"]["humidity"],
                "pressure_hpa": data["main"]["pressure"],
                "wind_speed_ms": data["wind"].get("speed", 0),
                "wind_direction_deg": data["wind"].get("deg", 0),
                "cloud_cover_percent": data["clouds"]["all"],
                "visibility_m": data.get("visibility", 10000),
                "weather_condition": data["weather"][0]["main"],
                "weather_description": data["weather"][0]["description"],
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"])
            }
            
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None
    
    def get_weather_forecast(self, lat: float, lon: float, days: int = 5) -> List[Dict[str, Any]]:
        """Get weather forecast for a location"""
        try:
            if not self.api_key:
                logger.warning("OpenWeatherMap API key not configured")
                return []
            
            url = self.forecast_url
            params = {
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": "metric",
                "cnt": min(days * 8, 40)  # 8 forecasts per day (3-hour intervals), max 40
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            forecasts = []
            
            for item in data["list"]:
                forecast = {
                    "timestamp": datetime.fromtimestamp(item["dt"]),
                    "temperature_c": item["main"]["temp"],
                    "humidity_percent": item["main"]["humidity"],
                    "pressure_hpa": item["main"]["pressure"],
                    "wind_speed_ms": item["wind"].get("speed", 0),
                    "wind_direction_deg": item["wind"].get("deg", 0),
                    "cloud_cover_percent": item["clouds"]["all"],
                    "weather_condition": item["weather"][0]["main"],
                    "weather_description": item["weather"][0]["description"],
                    "precipitation_mm": item.get("rain", {}).get("3h", 0) + item.get("snow", {}).get("3h", 0)
                }
                forecasts.append(forecast)
            
            return forecasts
            
        except Exception as e:
            logger.error(f"Error fetching weather forecast: {e}")
            return []
    
    def calculate_solar_irradiance(self, weather_data: Dict[str, Any]) -> float:
        """Calculate estimated solar irradiance from weather data"""
        try:
            # Base solar irradiance (clear sky at noon)
            base_irradiance = 1000  # W/m²
            
            # Cloud cover reduction factor
            cloud_cover = weather_data.get("cloud_cover_percent", 0) / 100
            cloud_factor = 1 - (cloud_cover * 0.75)  # Clouds reduce irradiance by up to 75%
            
            # Time of day factor (simplified)
            current_hour = weather_data["timestamp"].hour
            if 6 <= current_hour <= 18:
                # Simplified solar angle calculation
                solar_angle_factor = abs(12 - current_hour) / 6  # 0 at noon, 1 at 6am/6pm
                time_factor = 1 - (solar_angle_factor * 0.8)
            else:
                time_factor = 0  # No solar irradiance at night
            
            # Weather condition factor
            condition = weather_data.get("weather_condition", "Clear")
            condition_factors = {
                "Clear": 1.0,
                "Clouds": 0.8,
                "Rain": 0.3,
                "Snow": 0.2,
                "Thunderstorm": 0.2,
                "Drizzle": 0.5,
                "Mist": 0.7,
                "Fog": 0.4
            }
            condition_factor = condition_factors.get(condition, 0.8)
            
            # Calculate final irradiance
            irradiance = base_irradiance * cloud_factor * time_factor * condition_factor
            
            return max(0, irradiance)
            
        except Exception as e:
            logger.error(f"Error calculating solar irradiance: {e}")
            return 0
    
    def update_weather_data(self):
        """Update weather data for all renewable energy sources"""
        try:
            db = SessionLocal()
            
            # Get all solar panel and wind turbine locations
            from app.models.renewable_energy import SolarPanel, WindTurbine
            
            solar_panels = db.query(SolarPanel).filter(SolarPanel.is_active == True).all()
            wind_turbines = db.query(WindTurbine).filter(WindTurbine.is_active == True).all()
            
            # Update weather for solar panels
            for panel in solar_panels:
                weather_data = self.get_current_weather(panel.latitude, panel.longitude)
                if weather_data:
                    # Add solar irradiance calculation
                    weather_data["irradiance_wm2"] = self.calculate_solar_irradiance(weather_data)
                    
                    # Store weather data (you might want to create a weather_data table)
                    logger.debug(f"Updated weather for solar panel {panel.panel_id}: {weather_data}")
            
            # Update weather for wind turbines
            for turbine in wind_turbines:
                weather_data = self.get_current_weather(turbine.latitude, turbine.longitude)
                if weather_data:
                    logger.debug(f"Updated weather for wind turbine {turbine.turbine_id}: {weather_data}")
            
            db.close()
            logger.info("Weather data update completed")
            
        except Exception as e:
            logger.error(f"Error updating weather data: {e}")
    
    def get_weather_for_location(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get comprehensive weather data for a specific location"""
        current_weather = self.get_current_weather(lat, lon)
        forecast = self.get_weather_forecast(lat, lon)
        
        if current_weather:
            current_weather["irradiance_wm2"] = self.calculate_solar_irradiance(current_weather)
        
        return {
            "current": current_weather,
            "forecast": forecast,
            "location": {"latitude": lat, "longitude": lon},
            "updated_at": datetime.utcnow()
        }
    
    def get_historical_weather(self, lat: float, lon: float, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get historical weather data (requires paid OpenWeatherMap plan)"""
        # This would require the historical weather API
        # For now, return empty list as it requires a paid plan
        logger.warning("Historical weather data requires paid OpenWeatherMap plan")
        return []
    
    def calculate_wind_power_potential(self, wind_speed_ms: float, turbine_specs: Dict[str, float]) -> float:
        """Calculate wind power potential based on wind speed and turbine specifications"""
        try:
            cut_in_speed = turbine_specs.get("cut_in_speed_ms", 3.0)
            cut_out_speed = turbine_specs.get("cut_out_speed_ms", 25.0)
            rated_speed = turbine_specs.get("rated_speed_ms", 12.0)
            rated_power_kw = turbine_specs.get("capacity_kw", 1000.0)
            
            if wind_speed_ms < cut_in_speed or wind_speed_ms > cut_out_speed:
                return 0.0
            elif wind_speed_ms >= rated_speed:
                return rated_power_kw
            else:
                # Linear interpolation between cut-in and rated speed
                power_ratio = (wind_speed_ms - cut_in_speed) / (rated_speed - cut_in_speed)
                return rated_power_kw * power_ratio
                
        except Exception as e:
            logger.error(f"Error calculating wind power potential: {e}")
            return 0.0
