"""
Renewable energy data models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class SolarPanel(Base):
    """Solar panel installation model"""
    __tablename__ = "solar_panels"
    
    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(String(50), unique=True, index=True, nullable=False)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Technical specifications
    capacity_kw = Column(Float, nullable=False)  # Peak capacity in kW
    panel_area_m2 = Column(Float, nullable=False)  # Panel area in square meters
    efficiency = Column(Float, nullable=False)  # Panel efficiency (0-1)
    tilt_angle = Column(Float, nullable=False)  # Tilt angle in degrees
    azimuth_angle = Column(Float, nullable=False)  # Azimuth angle in degrees
    
    installation_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SolarPanel(panel_id='{self.panel_id}', capacity={self.capacity_kw}kW)>"


class WindTurbine(Base):
    """Wind turbine model"""
    __tablename__ = "wind_turbines"
    
    id = Column(Integer, primary_key=True, index=True)
    turbine_id = Column(String(50), unique=True, index=True, nullable=False)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Technical specifications
    capacity_kw = Column(Float, nullable=False)  # Rated capacity in kW
    rotor_diameter_m = Column(Float, nullable=False)  # Rotor diameter in meters
    hub_height_m = Column(Float, nullable=False)  # Hub height in meters
    cut_in_speed_ms = Column(Float, nullable=False)  # Cut-in wind speed m/s
    cut_out_speed_ms = Column(Float, nullable=False)  # Cut-out wind speed m/s
    rated_speed_ms = Column(Float, nullable=False)  # Rated wind speed m/s
    
    installation_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<WindTurbine(turbine_id='{self.turbine_id}', capacity={self.capacity_kw}kW)>"


class RenewableEnergyGeneration(Base):
    """Renewable energy generation data"""
    __tablename__ = "renewable_energy_generation"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(50), nullable=False, index=True)  # panel_id or turbine_id
    source_type = Column(String(20), nullable=False)  # solar, wind
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Generation data
    power_output_kw = Column(Float, nullable=False)  # Current power output
    energy_generated_kwh = Column(Float, nullable=False)  # Energy generated in interval
    
    # Environmental conditions
    irradiance_wm2 = Column(Float, nullable=True)  # Solar irradiance (for solar)
    wind_speed_ms = Column(Float, nullable=True)  # Wind speed (for wind)
    wind_direction_deg = Column(Float, nullable=True)  # Wind direction (for wind)
    temperature_c = Column(Float, nullable=True)  # Ambient temperature
    
    # Performance metrics
    capacity_factor = Column(Float, nullable=True)  # Actual/rated output ratio
    efficiency = Column(Float, nullable=True)  # Current efficiency
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<RenewableGeneration(source_id='{self.source_id}', type='{self.source_type}', power={self.power_output_kw}kW)>"


class RenewableForecast(Base):
    """Renewable energy generation forecast"""
    __tablename__ = "renewable_forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String(50), nullable=False, index=True)
    source_type = Column(String(20), nullable=False)  # solar, wind
    forecast_timestamp = Column(DateTime, nullable=False, index=True)
    target_timestamp = Column(DateTime, nullable=False, index=True)
    
    # Forecast data
    predicted_power_kw = Column(Float, nullable=False)
    predicted_energy_kwh = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)
    
    # Weather forecast inputs
    predicted_irradiance_wm2 = Column(Float, nullable=True)  # For solar
    predicted_wind_speed_ms = Column(Float, nullable=True)  # For wind
    predicted_temperature_c = Column(Float, nullable=True)
    predicted_cloud_cover = Column(Float, nullable=True)  # 0-1
    
    # Model information
    model_version = Column(String(50), nullable=False)
    forecast_accuracy = Column(Float, nullable=True)  # When actual data is available
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<RenewableForecast(source_id='{self.source_id}', target='{self.target_timestamp}', predicted={self.predicted_power_kw}kW)>"
