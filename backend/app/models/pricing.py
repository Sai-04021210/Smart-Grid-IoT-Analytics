"""
Energy pricing and market data models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class EnergyPrice(Base):
    """Energy pricing model"""
    __tablename__ = "energy_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # Pricing tiers
    base_price_kwh = Column(Float, nullable=False)  # Base price per kWh
    peak_price_kwh = Column(Float, nullable=False)  # Peak hour price
    off_peak_price_kwh = Column(Float, nullable=False)  # Off-peak price
    
    # Time-of-use periods
    peak_start_hour = Column(Integer, nullable=False, default=17)  # 5 PM
    peak_end_hour = Column(Integer, nullable=False, default=21)    # 9 PM
    
    # Demand charges
    demand_charge_kw = Column(Float, nullable=True)  # Demand charge per kW
    
    # Seasonal adjustments
    season = Column(String(20), nullable=False)  # summer, winter, spring, fall
    seasonal_multiplier = Column(Float, nullable=False, default=1.0)
    
    # Market conditions
    wholesale_price = Column(Float, nullable=True)  # Wholesale market price
    transmission_cost = Column(Float, nullable=True)  # Transmission costs
    distribution_cost = Column(Float, nullable=True)  # Distribution costs
    
    # Renewable energy credits
    renewable_credit_price = Column(Float, nullable=True)
    carbon_credit_price = Column(Float, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<EnergyPrice(timestamp='{self.timestamp}', base_price={self.base_price_kwh})>"


class DynamicPricing(Base):
    """Dynamic pricing optimization results"""
    __tablename__ = "dynamic_pricing"
    
    id = Column(Integer, primary_key=True, index=True)
    optimization_timestamp = Column(DateTime, nullable=False, index=True)
    target_timestamp = Column(DateTime, nullable=False, index=True)
    
    # Optimized pricing
    optimized_price_kwh = Column(Float, nullable=False)
    price_adjustment_factor = Column(Float, nullable=False)  # Multiplier from base price
    
    # Market conditions that influenced pricing
    predicted_demand_kw = Column(Float, nullable=False)
    predicted_supply_kw = Column(Float, nullable=False)
    renewable_generation_kw = Column(Float, nullable=True)
    grid_congestion_level = Column(Float, nullable=True)  # 0-1 scale
    
    # Optimization objectives
    revenue_optimization = Column(Float, nullable=True)  # Expected revenue
    demand_response_factor = Column(Float, nullable=True)  # Demand shaping effect
    grid_stability_score = Column(Float, nullable=True)  # Grid stability impact
    
    # Algorithm details
    optimization_algorithm = Column(String(50), nullable=False)
    convergence_iterations = Column(Integer, nullable=True)
    optimization_confidence = Column(Float, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<DynamicPricing(target='{self.target_timestamp}', price={self.optimized_price_kwh})>"


class MarketData(Base):
    """Energy market data"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    market_region = Column(String(50), nullable=False)
    
    # Wholesale market prices
    day_ahead_price = Column(Float, nullable=True)  # Day-ahead market price
    real_time_price = Column(Float, nullable=True)  # Real-time market price
    ancillary_services_price = Column(Float, nullable=True)
    
    # Supply and demand
    total_demand_mw = Column(Float, nullable=True)
    total_supply_mw = Column(Float, nullable=True)
    renewable_supply_mw = Column(Float, nullable=True)
    fossil_supply_mw = Column(Float, nullable=True)
    
    # Grid conditions
    frequency_hz = Column(Float, nullable=True)  # Grid frequency
    voltage_stability = Column(Float, nullable=True)  # Voltage stability index
    transmission_congestion = Column(JSON, nullable=True)  # Congestion by line
    
    # Weather impact
    temperature_c = Column(Float, nullable=True)
    humidity_percent = Column(Float, nullable=True)
    wind_speed_ms = Column(Float, nullable=True)
    solar_irradiance_wm2 = Column(Float, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<MarketData(timestamp='{self.timestamp}', region='{self.market_region}')>"


class CustomerBilling(Base):
    """Customer billing information"""
    __tablename__ = "customer_billing"
    
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(String(50), nullable=False, index=True)
    billing_period_start = Column(DateTime, nullable=False)
    billing_period_end = Column(DateTime, nullable=False)
    
    # Energy consumption
    total_energy_kwh = Column(Float, nullable=False)
    peak_energy_kwh = Column(Float, nullable=False)
    off_peak_energy_kwh = Column(Float, nullable=False)
    
    # Demand charges
    peak_demand_kw = Column(Float, nullable=True)
    demand_charge = Column(Float, nullable=True)
    
    # Billing amounts
    energy_charges = Column(Float, nullable=False)
    demand_charges = Column(Float, nullable=False, default=0.0)
    transmission_charges = Column(Float, nullable=False, default=0.0)
    distribution_charges = Column(Float, nullable=False, default=0.0)
    taxes_and_fees = Column(Float, nullable=False, default=0.0)
    total_amount = Column(Float, nullable=False)
    
    # Payment information
    due_date = Column(DateTime, nullable=False)
    payment_status = Column(String(20), nullable=False, default="pending")  # pending, paid, overdue
    payment_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<CustomerBilling(meter_id='{self.meter_id}', period='{self.billing_period_start}', amount={self.total_amount})>"
