"""
Smart Meter data models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SmartMeter(Base):
    """Smart meter device model"""
    __tablename__ = "smart_meters"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String(50), unique=True, index=True, nullable=False)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    meter_type = Column(String(50), nullable=False)  # residential, commercial, industrial
    installation_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    firmware_version = Column(String(20), nullable=True)
    last_communication = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    readings = relationship("EnergyReading", back_populates="meter")
    
    def __repr__(self):
        return f"<SmartMeter(meter_id='{self.meter_id}', location='{self.location}')>"


class EnergyReading(Base):
    """Energy consumption reading model"""
    __tablename__ = "energy_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String(50), ForeignKey("smart_meters.meter_id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Energy measurements (kWh)
    active_energy = Column(Float, nullable=False)  # Total active energy
    reactive_energy = Column(Float, nullable=True)  # Reactive energy
    apparent_energy = Column(Float, nullable=True)  # Apparent energy
    
    # Power measurements (kW)
    active_power = Column(Float, nullable=True)  # Instantaneous active power
    reactive_power = Column(Float, nullable=True)  # Reactive power
    power_factor = Column(Float, nullable=True)  # Power factor
    
    # Voltage and current
    voltage_l1 = Column(Float, nullable=True)  # Line 1 voltage
    voltage_l2 = Column(Float, nullable=True)  # Line 2 voltage
    voltage_l3 = Column(Float, nullable=True)  # Line 3 voltage
    current_l1 = Column(Float, nullable=True)  # Line 1 current
    current_l2 = Column(Float, nullable=True)  # Line 2 current
    current_l3 = Column(Float, nullable=True)  # Line 3 current
    
    # Frequency
    frequency = Column(Float, nullable=True)
    
    # Data quality
    quality_flag = Column(String(20), default="good")  # good, estimated, missing
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    meter = relationship("SmartMeter", back_populates="readings")
    
    def __repr__(self):
        return f"<EnergyReading(meter_id='{self.meter_id}', timestamp='{self.timestamp}', active_energy={self.active_energy})>"


class EnergyPrediction(Base):
    """Energy consumption prediction model"""
    __tablename__ = "energy_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String(50), ForeignKey("smart_meters.meter_id"), nullable=False)
    prediction_timestamp = Column(DateTime, nullable=False, index=True)
    target_timestamp = Column(DateTime, nullable=False, index=True)
    
    # Predictions
    predicted_consumption = Column(Float, nullable=False)  # kWh
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)
    prediction_accuracy = Column(Float, nullable=True)  # When actual data is available
    
    # Model information
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # lstm, arima, etc.
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<EnergyPrediction(meter_id='{self.meter_id}', target='{self.target_timestamp}', predicted={self.predicted_consumption})>"
