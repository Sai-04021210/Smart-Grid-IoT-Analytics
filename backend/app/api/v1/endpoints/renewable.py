"""
Renewable energy API endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.renewable_energy import (
    SolarPanel, WindTurbine, RenewableEnergyGeneration, RenewableForecast
)

router = APIRouter()


@router.get("/solar/generation")
async def get_solar_generation(
    panel_id: Optional[str] = Query(None, description="Filter by panel ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, le=1000, description="Maximum records"),
    db: Session = Depends(get_db)
):
    """Get solar generation data"""
    
    query = db.query(RenewableEnergyGeneration).filter(
        RenewableEnergyGeneration.source_type == "solar"
    )
    
    if panel_id:
        query = query.filter(RenewableEnergyGeneration.source_id == panel_id)
    
    if start_date:
        query = query.filter(RenewableEnergyGeneration.timestamp >= start_date)
    
    if end_date:
        query = query.filter(RenewableEnergyGeneration.timestamp <= end_date)
    
    generation_data = query.order_by(
        RenewableEnergyGeneration.timestamp.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": gen.id,
            "source_id": gen.source_id,
            "timestamp": gen.timestamp,
            "power_output_kw": gen.power_output_kw,
            "energy_generated_kwh": gen.energy_generated_kwh,
            "irradiance_wm2": gen.irradiance_wm2,
            "temperature_c": gen.temperature_c,
            "capacity_factor": gen.capacity_factor,
            "efficiency": gen.efficiency
        }
        for gen in generation_data
    ]


@router.get("/wind/generation")
async def get_wind_generation(
    turbine_id: Optional[str] = Query(None, description="Filter by turbine ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, le=1000, description="Maximum records"),
    db: Session = Depends(get_db)
):
    """Get wind generation data"""
    
    query = db.query(RenewableEnergyGeneration).filter(
        RenewableEnergyGeneration.source_type == "wind"
    )
    
    if turbine_id:
        query = query.filter(RenewableEnergyGeneration.source_id == turbine_id)
    
    if start_date:
        query = query.filter(RenewableEnergyGeneration.timestamp >= start_date)
    
    if end_date:
        query = query.filter(RenewableEnergyGeneration.timestamp <= end_date)
    
    generation_data = query.order_by(
        RenewableEnergyGeneration.timestamp.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": gen.id,
            "source_id": gen.source_id,
            "timestamp": gen.timestamp,
            "power_output_kw": gen.power_output_kw,
            "energy_generated_kwh": gen.energy_generated_kwh,
            "wind_speed_ms": gen.wind_speed_ms,
            "wind_direction_deg": gen.wind_direction_deg,
            "temperature_c": gen.temperature_c,
            "capacity_factor": gen.capacity_factor,
            "efficiency": gen.efficiency
        }
        for gen in generation_data
    ]


@router.get("/forecasts")
async def get_renewable_forecasts(
    source_type: str = Query(..., regex="^(solar|wind)$", description="Source type"),
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours to forecast"),
    db: Session = Depends(get_db)
):
    """Get renewable energy forecasts"""
    
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=hours_ahead)
    
    forecasts = db.query(RenewableForecast).filter(
        RenewableForecast.source_type == source_type,
        RenewableForecast.target_timestamp >= start_time,
        RenewableForecast.target_timestamp <= end_time
    ).order_by(RenewableForecast.target_timestamp.asc()).all()
    
    return [
        {
            "source_id": forecast.source_id,
            "source_type": forecast.source_type,
            "timestamp": forecast.target_timestamp,
            "predicted_power_kw": forecast.predicted_power_kw,
            "predicted_energy_kwh": forecast.predicted_energy_kwh,
            "confidence_lower": forecast.confidence_interval_lower,
            "confidence_upper": forecast.confidence_interval_upper,
            "predicted_irradiance_wm2": forecast.predicted_irradiance_wm2,
            "predicted_wind_speed_ms": forecast.predicted_wind_speed_ms,
            "predicted_temperature_c": forecast.predicted_temperature_c
        }
        for forecast in forecasts
    ]


@router.get("/summary")
async def get_renewable_summary(
    period: str = Query("day", regex="^(hour|day|week|month)$"),
    db: Session = Depends(get_db)
):
    """Get renewable energy generation summary"""
    
    # Calculate time range
    now = datetime.utcnow()
    if period == "hour":
        start_time = now - timedelta(hours=24)
    elif period == "day":
        start_time = now - timedelta(days=7)
    elif period == "week":
        start_time = now - timedelta(weeks=4)
    else:  # month
        start_time = now - timedelta(days=365)
    
    # Get solar summary
    solar_summary = db.query(
        func.sum(RenewableEnergyGeneration.energy_generated_kwh).label("total_energy"),
        func.avg(RenewableEnergyGeneration.power_output_kw).label("avg_power"),
        func.max(RenewableEnergyGeneration.power_output_kw).label("peak_power"),
        func.avg(RenewableEnergyGeneration.capacity_factor).label("avg_capacity_factor")
    ).filter(
        RenewableEnergyGeneration.source_type == "solar",
        RenewableEnergyGeneration.timestamp >= start_time
    ).first()
    
    # Get wind summary
    wind_summary = db.query(
        func.sum(RenewableEnergyGeneration.energy_generated_kwh).label("total_energy"),
        func.avg(RenewableEnergyGeneration.power_output_kw).label("avg_power"),
        func.max(RenewableEnergyGeneration.power_output_kw).label("peak_power"),
        func.avg(RenewableEnergyGeneration.capacity_factor).label("avg_capacity_factor")
    ).filter(
        RenewableEnergyGeneration.source_type == "wind",
        RenewableEnergyGeneration.timestamp >= start_time
    ).first()
    
    return {
        "period": period,
        "start_time": start_time,
        "end_time": now,
        "solar": {
            "total_energy_kwh": float(solar_summary.total_energy or 0),
            "average_power_kw": float(solar_summary.avg_power or 0),
            "peak_power_kw": float(solar_summary.peak_power or 0),
            "average_capacity_factor": float(solar_summary.avg_capacity_factor or 0)
        },
        "wind": {
            "total_energy_kwh": float(wind_summary.total_energy or 0),
            "average_power_kw": float(wind_summary.avg_power or 0),
            "peak_power_kw": float(wind_summary.peak_power or 0),
            "average_capacity_factor": float(wind_summary.avg_capacity_factor or 0)
        }
    }


@router.get("/panels")
async def get_solar_panels(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get solar panel information"""
    
    query = db.query(SolarPanel)
    
    if is_active is not None:
        query = query.filter(SolarPanel.is_active == is_active)
    
    panels = query.all()
    
    return [
        {
            "panel_id": panel.panel_id,
            "location": panel.location,
            "latitude": panel.latitude,
            "longitude": panel.longitude,
            "capacity_kw": panel.capacity_kw,
            "panel_area_m2": panel.panel_area_m2,
            "efficiency": panel.efficiency,
            "tilt_angle": panel.tilt_angle,
            "azimuth_angle": panel.azimuth_angle,
            "installation_date": panel.installation_date,
            "is_active": panel.is_active
        }
        for panel in panels
    ]


@router.get("/turbines")
async def get_wind_turbines(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get wind turbine information"""
    
    query = db.query(WindTurbine)
    
    if is_active is not None:
        query = query.filter(WindTurbine.is_active == is_active)
    
    turbines = query.all()
    
    return [
        {
            "turbine_id": turbine.turbine_id,
            "location": turbine.location,
            "latitude": turbine.latitude,
            "longitude": turbine.longitude,
            "capacity_kw": turbine.capacity_kw,
            "rotor_diameter_m": turbine.rotor_diameter_m,
            "hub_height_m": turbine.hub_height_m,
            "cut_in_speed_ms": turbine.cut_in_speed_ms,
            "cut_out_speed_ms": turbine.cut_out_speed_ms,
            "rated_speed_ms": turbine.rated_speed_ms,
            "installation_date": turbine.installation_date,
            "is_active": turbine.is_active
        }
        for turbine in turbines
    ]
