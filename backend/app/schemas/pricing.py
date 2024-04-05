"""
Pricing-related Pydantic schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CurrentPriceResponse(BaseModel):
    """Schema for current price response"""
    price_per_kwh: float = Field(..., description="Current price per kWh")
    meter_type: str = Field(..., description="Type of meter")
    timestamp: datetime = Field(..., description="Price timestamp")
    pricing_tier: str = Field(..., description="Current pricing tier")


class PriceForecastResponse(BaseModel):
    """Schema for price forecast response"""
    timestamp: datetime = Field(..., description="Forecast timestamp")
    price_per_kwh: float = Field(..., description="Forecasted price per kWh")
    adjustment_factor: float = Field(..., description="Price adjustment factor")
    predicted_demand: float = Field(..., description="Predicted demand in kW")
    renewable_generation: float = Field(..., description="Renewable generation in kW")


class PricingOptimizationResponse(BaseModel):
    """Schema for pricing optimization response"""
    target_timestamp: datetime = Field(..., description="Target timestamp")
    optimized_price_kwh: float = Field(..., description="Optimized price per kWh")
    adjustment_factor: float = Field(..., description="Price adjustment factor")
    predicted_demand_kw: float = Field(..., description="Predicted demand in kW")
    predicted_supply_kw: float = Field(..., description="Predicted supply in kW")
    renewable_generation_kw: Optional[float] = Field(None, description="Renewable generation in kW")
    optimization_algorithm: str = Field(..., description="Algorithm used")
    optimization_confidence: Optional[float] = Field(None, description="Optimization confidence")
    created_at: datetime = Field(..., description="Creation timestamp")


class EnergyPriceBase(BaseModel):
    """Base schema for energy prices"""
    timestamp: datetime = Field(..., description="Price timestamp")
    base_price_kwh: float = Field(..., description="Base price per kWh")
    peak_price_kwh: float = Field(..., description="Peak hour price per kWh")
    off_peak_price_kwh: float = Field(..., description="Off-peak price per kWh")
    peak_start_hour: int = Field(17, ge=0, le=23, description="Peak period start hour")
    peak_end_hour: int = Field(21, ge=0, le=23, description="Peak period end hour")
    season: str = Field(..., description="Current season")
    seasonal_multiplier: float = Field(1.0, description="Seasonal adjustment factor")


class EnergyPriceCreate(EnergyPriceBase):
    """Schema for creating energy prices"""
    wholesale_price: Optional[float] = Field(None, description="Wholesale market price")
    transmission_cost: Optional[float] = Field(None, description="Transmission costs")
    distribution_cost: Optional[float] = Field(None, description="Distribution costs")
    renewable_credit_price: Optional[float] = Field(None, description="Renewable energy credit price")
    carbon_credit_price: Optional[float] = Field(None, description="Carbon credit price")


class EnergyPriceResponse(EnergyPriceBase):
    """Schema for energy price responses"""
    id: int
    wholesale_price: Optional[float]
    transmission_cost: Optional[float]
    distribution_cost: Optional[float]
    renewable_credit_price: Optional[float]
    carbon_credit_price: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DynamicPricingBase(BaseModel):
    """Base schema for dynamic pricing"""
    optimization_timestamp: datetime = Field(..., description="When optimization was run")
    target_timestamp: datetime = Field(..., description="Target time for pricing")
    optimized_price_kwh: float = Field(..., description="Optimized price per kWh")
    price_adjustment_factor: float = Field(..., description="Adjustment factor from base price")
    predicted_demand_kw: float = Field(..., description="Predicted demand in kW")
    predicted_supply_kw: float = Field(..., description="Predicted supply in kW")
    renewable_generation_kw: Optional[float] = Field(None, description="Renewable generation in kW")
    grid_congestion_level: Optional[float] = Field(None, description="Grid congestion level (0-1)")
    optimization_algorithm: str = Field(..., description="Algorithm used for optimization")


class DynamicPricingCreate(DynamicPricingBase):
    """Schema for creating dynamic pricing records"""
    revenue_optimization: Optional[float] = Field(None, description="Expected revenue")
    demand_response_factor: Optional[float] = Field(None, description="Demand response effect")
    grid_stability_score: Optional[float] = Field(None, description="Grid stability impact")
    convergence_iterations: Optional[int] = Field(None, description="Algorithm iterations")
    optimization_confidence: Optional[float] = Field(None, description="Confidence level")


class DynamicPricingResponse(DynamicPricingBase):
    """Schema for dynamic pricing responses"""
    id: int
    revenue_optimization: Optional[float]
    demand_response_factor: Optional[float]
    grid_stability_score: Optional[float]
    convergence_iterations: Optional[int]
    optimization_confidence: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarketDataBase(BaseModel):
    """Base schema for market data"""
    timestamp: datetime = Field(..., description="Market data timestamp")
    market_region: str = Field(..., description="Market region identifier")
    day_ahead_price: Optional[float] = Field(None, description="Day-ahead market price")
    real_time_price: Optional[float] = Field(None, description="Real-time market price")
    ancillary_services_price: Optional[float] = Field(None, description="Ancillary services price")
    total_demand_mw: Optional[float] = Field(None, description="Total demand in MW")
    total_supply_mw: Optional[float] = Field(None, description="Total supply in MW")
    renewable_supply_mw: Optional[float] = Field(None, description="Renewable supply in MW")
    fossil_supply_mw: Optional[float] = Field(None, description="Fossil fuel supply in MW")


class MarketDataCreate(MarketDataBase):
    """Schema for creating market data"""
    frequency_hz: Optional[float] = Field(None, description="Grid frequency in Hz")
    voltage_stability: Optional[float] = Field(None, description="Voltage stability index")
    temperature_c: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity_percent: Optional[float] = Field(None, description="Humidity percentage")
    wind_speed_ms: Optional[float] = Field(None, description="Wind speed in m/s")
    solar_irradiance_wm2: Optional[float] = Field(None, description="Solar irradiance in W/m²")


class MarketDataResponse(MarketDataBase):
    """Schema for market data responses"""
    id: int
    frequency_hz: Optional[float]
    voltage_stability: Optional[float]
    temperature_c: Optional[float]
    humidity_percent: Optional[float]
    wind_speed_ms: Optional[float]
    solar_irradiance_wm2: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True
