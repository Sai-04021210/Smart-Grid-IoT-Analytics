"""
Energy-related Pydantic schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class EnergyReadingBase(BaseModel):
    """Base schema for energy readings"""
    meter_id: str
    timestamp: datetime
    active_energy: float = Field(..., description="Active energy in kWh")
    reactive_energy: Optional[float] = Field(None, description="Reactive energy in kVArh")
    apparent_energy: Optional[float] = Field(None, description="Apparent energy in kVAh")
    active_power: Optional[float] = Field(None, description="Active power in kW")
    reactive_power: Optional[float] = Field(None, description="Reactive power in kVAr")
    power_factor: Optional[float] = Field(None, ge=0, le=1, description="Power factor")
    voltage_l1: Optional[float] = Field(None, description="Line 1 voltage in V")
    voltage_l2: Optional[float] = Field(None, description="Line 2 voltage in V")
    voltage_l3: Optional[float] = Field(None, description="Line 3 voltage in V")
    current_l1: Optional[float] = Field(None, description="Line 1 current in A")
    current_l2: Optional[float] = Field(None, description="Line 2 current in A")
    current_l3: Optional[float] = Field(None, description="Line 3 current in A")
    frequency: Optional[float] = Field(None, description="Frequency in Hz")
    quality_flag: str = Field("good", description="Data quality flag")


class EnergyReadingCreate(EnergyReadingBase):
    """Schema for creating energy readings"""
    pass


class EnergyReadingResponse(EnergyReadingBase):
    """Schema for energy reading responses"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EnergyConsumptionSummary(BaseModel):
    """Schema for energy consumption summary"""
    total_consumption: float = Field(..., description="Total consumption in kWh")
    average_power: float = Field(..., description="Average power in kW")
    peak_power: float = Field(..., description="Peak power in kW")
    reading_count: int = Field(..., description="Number of readings")
    period: str = Field(..., description="Aggregation period")
    start_time: datetime = Field(..., description="Start of period")
    end_time: datetime = Field(..., description="End of period")


class SmartMeterBase(BaseModel):
    """Base schema for smart meters"""
    meter_id: str = Field(..., description="Unique meter identifier")
    location: str = Field(..., description="Meter location")
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")
    meter_type: str = Field(..., description="Type of meter (residential, commercial, industrial)")
    installation_date: datetime = Field(..., description="Installation date")
    firmware_version: Optional[str] = Field(None, description="Firmware version")


class SmartMeterCreate(SmartMeterBase):
    """Schema for creating smart meters"""
    pass


class SmartMeterResponse(SmartMeterBase):
    """Schema for smart meter responses"""
    id: int
    is_active: bool
    last_communication: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EnergyPredictionBase(BaseModel):
    """Base schema for energy predictions"""
    meter_id: str
    prediction_timestamp: datetime
    target_timestamp: datetime
    predicted_consumption: float = Field(..., description="Predicted consumption in kWh")
    confidence_interval_lower: Optional[float] = Field(None, description="Lower confidence bound")
    confidence_interval_upper: Optional[float] = Field(None, description="Upper confidence bound")
    model_version: str = Field(..., description="Model version used")
    model_type: str = Field(..., description="Type of model (lstm, arima, etc.)")


class EnergyPredictionResponse(EnergyPredictionBase):
    """Schema for energy prediction responses"""
    id: int
    prediction_accuracy: Optional[float] = Field(None, description="Prediction accuracy when available")
    created_at: datetime
    
    class Config:
        from_attributes = True
