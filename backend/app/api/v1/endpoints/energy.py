"""
Energy consumption API endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.smart_meter import EnergyReading, SmartMeter
from app.schemas.energy import EnergyReadingResponse, EnergyConsumptionSummary

router = APIRouter()


@router.get("/consumption", response_model=List[EnergyReadingResponse])
async def get_energy_consumption(
    meter_id: Optional[str] = Query(None, description="Filter by meter ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for data range"),
    end_date: Optional[datetime] = Query(None, description="End date for data range"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """Get energy consumption data"""
    
    query = db.query(EnergyReading)
    
    # Apply filters
    if meter_id:
        query = query.filter(EnergyReading.meter_id == meter_id)
    
    if start_date:
        query = query.filter(EnergyReading.timestamp >= start_date)
    
    if end_date:
        query = query.filter(EnergyReading.timestamp <= end_date)
    
    # Order by timestamp and limit
    readings = query.order_by(EnergyReading.timestamp.desc()).limit(limit).all()
    
    return readings


@router.get("/consumption/summary", response_model=EnergyConsumptionSummary)
async def get_consumption_summary(
    meter_id: Optional[str] = Query(None, description="Filter by meter ID"),
    period: str = Query("day", regex="^(hour|day|week|month)$", description="Aggregation period"),
    db: Session = Depends(get_db)
):
    """Get energy consumption summary"""
    
    # Calculate time range based on period
    now = datetime.utcnow()
    if period == "hour":
        start_time = now - timedelta(hours=24)
    elif period == "day":
        start_time = now - timedelta(days=7)
    elif period == "week":
        start_time = now - timedelta(weeks=4)
    else:  # month
        start_time = now - timedelta(days=365)
    
    query = db.query(
        func.sum(EnergyReading.active_energy).label("total_consumption"),
        func.avg(EnergyReading.active_power).label("avg_power"),
        func.max(EnergyReading.active_power).label("peak_power"),
        func.count(EnergyReading.id).label("reading_count")
    ).filter(EnergyReading.timestamp >= start_time)
    
    if meter_id:
        query = query.filter(EnergyReading.meter_id == meter_id)
    
    result = query.first()
    
    return EnergyConsumptionSummary(
        total_consumption=result.total_consumption or 0,
        average_power=result.avg_power or 0,
        peak_power=result.peak_power or 0,
        reading_count=result.reading_count or 0,
        period=period,
        start_time=start_time,
        end_time=now
    )


@router.get("/meters", response_model=List[dict])
async def get_smart_meters(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    meter_type: Optional[str] = Query(None, description="Filter by meter type"),
    db: Session = Depends(get_db)
):
    """Get list of smart meters"""
    
    query = db.query(SmartMeter)
    
    if is_active is not None:
        query = query.filter(SmartMeter.is_active == is_active)
    
    if meter_type:
        query = query.filter(SmartMeter.meter_type == meter_type)
    
    meters = query.all()
    
    return [
        {
            "meter_id": meter.meter_id,
            "location": meter.location,
            "meter_type": meter.meter_type,
            "is_active": meter.is_active,
            "last_communication": meter.last_communication,
            "installation_date": meter.installation_date
        }
        for meter in meters
    ]


@router.get("/consumption/hourly")
async def get_hourly_consumption(
    meter_id: Optional[str] = Query(None, description="Filter by meter ID"),
    days: int = Query(7, le=30, description="Number of days to include"),
    db: Session = Depends(get_db)
):
    """Get hourly energy consumption aggregated data"""
    
    start_time = datetime.utcnow() - timedelta(days=days)
    
    # Group by hour and sum consumption
    query = db.query(
        func.date_trunc('hour', EnergyReading.timestamp).label('hour'),
        func.sum(EnergyReading.active_energy).label('total_consumption'),
        func.avg(EnergyReading.active_power).label('avg_power'),
        func.count(EnergyReading.id).label('reading_count')
    ).filter(EnergyReading.timestamp >= start_time)
    
    if meter_id:
        query = query.filter(EnergyReading.meter_id == meter_id)
    
    results = query.group_by(
        func.date_trunc('hour', EnergyReading.timestamp)
    ).order_by('hour').all()
    
    return [
        {
            "timestamp": result.hour,
            "total_consumption": float(result.total_consumption or 0),
            "average_power": float(result.avg_power or 0),
            "reading_count": result.reading_count
        }
        for result in results
    ]


@router.get("/consumption/peak-hours")
async def get_peak_hours(
    meter_id: Optional[str] = Query(None, description="Filter by meter ID"),
    days: int = Query(30, le=90, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get peak consumption hours analysis"""
    
    start_time = datetime.utcnow() - timedelta(days=days)
    
    # Get hourly averages
    query = db.query(
        func.extract('hour', EnergyReading.timestamp).label('hour'),
        func.avg(EnergyReading.active_power).label('avg_power'),
        func.max(EnergyReading.active_power).label('max_power')
    ).filter(EnergyReading.timestamp >= start_time)
    
    if meter_id:
        query = query.filter(EnergyReading.meter_id == meter_id)
    
    results = query.group_by(
        func.extract('hour', EnergyReading.timestamp)
    ).order_by('hour').all()
    
    peak_hours = []
    for result in results:
        peak_hours.append({
            "hour": int(result.hour),
            "average_power": float(result.avg_power or 0),
            "peak_power": float(result.max_power or 0)
        })
    
    # Sort by average power to identify peak hours
    peak_hours.sort(key=lambda x: x["average_power"], reverse=True)
    
    return {
        "peak_hours": peak_hours[:5],  # Top 5 peak hours
        "analysis_period_days": days,
        "total_hours_analyzed": len(peak_hours)
    }
