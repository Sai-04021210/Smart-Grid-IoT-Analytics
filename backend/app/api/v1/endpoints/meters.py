"""
Smart meter management API endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models.smart_meter import SmartMeter, EnergyReading
from app.schemas.energy import SmartMeterCreate, SmartMeterResponse, EnergyReadingCreate

router = APIRouter()


@router.post("/register", response_model=SmartMeterResponse)
async def register_smart_meter(
    meter_data: SmartMeterCreate,
    db: Session = Depends(get_db)
):
    """Register a new smart meter"""
    
    # Check if meter already exists
    existing_meter = db.query(SmartMeter).filter(
        SmartMeter.meter_id == meter_data.meter_id
    ).first()
    
    if existing_meter:
        raise HTTPException(
            status_code=400, 
            detail=f"Meter with ID {meter_data.meter_id} already exists"
        )
    
    # Create new meter
    new_meter = SmartMeter(
        meter_id=meter_data.meter_id,
        location=meter_data.location,
        latitude=meter_data.latitude,
        longitude=meter_data.longitude,
        meter_type=meter_data.meter_type,
        installation_date=meter_data.installation_date,
        firmware_version=meter_data.firmware_version,
        is_active=True
    )
    
    db.add(new_meter)
    db.commit()
    db.refresh(new_meter)
    
    return new_meter


@router.post("/data")
async def submit_meter_reading(
    reading_data: EnergyReadingCreate,
    db: Session = Depends(get_db)
):
    """Submit energy reading data"""
    
    # Verify meter exists
    meter = db.query(SmartMeter).filter(
        SmartMeter.meter_id == reading_data.meter_id
    ).first()
    
    if not meter:
        raise HTTPException(
            status_code=404,
            detail=f"Meter {reading_data.meter_id} not found"
        )
    
    # Create energy reading
    new_reading = EnergyReading(**reading_data.dict())
    db.add(new_reading)
    
    # Update meter last communication
    meter.last_communication = datetime.utcnow()
    
    db.commit()
    db.refresh(new_reading)
    
    return {
        "id": new_reading.id,
        "meter_id": new_reading.meter_id,
        "timestamp": new_reading.timestamp,
        "status": "created"
    }


@router.get("/", response_model=List[SmartMeterResponse])
async def get_smart_meters(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    meter_type: Optional[str] = Query(None, description="Filter by meter type"),
    location: Optional[str] = Query(None, description="Filter by location"),
    db: Session = Depends(get_db)
):
    """Get list of smart meters"""
    
    query = db.query(SmartMeter)
    
    if is_active is not None:
        query = query.filter(SmartMeter.is_active == is_active)
    
    if meter_type:
        query = query.filter(SmartMeter.meter_type == meter_type)
    
    if location:
        query = query.filter(SmartMeter.location.ilike(f"%{location}%"))
    
    meters = query.all()
    return meters


@router.get("/{meter_id}", response_model=SmartMeterResponse)
async def get_smart_meter(
    meter_id: str,
    db: Session = Depends(get_db)
):
    """Get specific smart meter details"""
    
    meter = db.query(SmartMeter).filter(SmartMeter.meter_id == meter_id).first()
    
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    
    return meter


@router.put("/{meter_id}")
async def update_smart_meter(
    meter_id: str,
    meter_data: SmartMeterCreate,
    db: Session = Depends(get_db)
):
    """Update smart meter information"""
    
    meter = db.query(SmartMeter).filter(SmartMeter.meter_id == meter_id).first()
    
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    
    # Update meter fields
    for field, value in meter_data.dict(exclude_unset=True).items():
        setattr(meter, field, value)
    
    meter.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(meter)
    
    return meter


@router.delete("/{meter_id}")
async def deactivate_smart_meter(
    meter_id: str,
    db: Session = Depends(get_db)
):
    """Deactivate a smart meter"""
    
    meter = db.query(SmartMeter).filter(SmartMeter.meter_id == meter_id).first()
    
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    
    meter.is_active = False
    meter.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"Meter {meter_id} deactivated successfully"}


@router.get("/{meter_id}/status")
async def get_meter_status(
    meter_id: str,
    db: Session = Depends(get_db)
):
    """Get meter status and health information"""
    
    meter = db.query(SmartMeter).filter(SmartMeter.meter_id == meter_id).first()
    
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    
    # Get latest reading
    latest_reading = db.query(EnergyReading).filter(
        EnergyReading.meter_id == meter_id
    ).order_by(EnergyReading.timestamp.desc()).first()
    
    # Calculate communication status
    now = datetime.utcnow()
    if meter.last_communication:
        time_since_last = (now - meter.last_communication).total_seconds() / 60  # minutes
        if time_since_last <= 30:
            comm_status = "online"
        elif time_since_last <= 120:
            comm_status = "warning"
        else:
            comm_status = "offline"
    else:
        comm_status = "unknown"
    
    # Get reading count for last 24 hours
    yesterday = now - timedelta(hours=24)
    reading_count = db.query(func.count(EnergyReading.id)).filter(
        EnergyReading.meter_id == meter_id,
        EnergyReading.timestamp >= yesterday
    ).scalar()
    
    return {
        "meter_id": meter_id,
        "is_active": meter.is_active,
        "communication_status": comm_status,
        "last_communication": meter.last_communication,
        "latest_reading": {
            "timestamp": latest_reading.timestamp if latest_reading else None,
            "active_energy": latest_reading.active_energy if latest_reading else None,
            "active_power": latest_reading.active_power if latest_reading else None,
            "quality_flag": latest_reading.quality_flag if latest_reading else None
        } if latest_reading else None,
        "readings_24h": reading_count,
        "firmware_version": meter.firmware_version,
        "installation_date": meter.installation_date
    }


@router.get("/{meter_id}/readings")
async def get_meter_readings(
    meter_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(100, le=1000, description="Maximum records"),
    db: Session = Depends(get_db)
):
    """Get readings for a specific meter"""
    
    # Verify meter exists
    meter = db.query(SmartMeter).filter(SmartMeter.meter_id == meter_id).first()
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    
    query = db.query(EnergyReading).filter(EnergyReading.meter_id == meter_id)
    
    if start_date:
        query = query.filter(EnergyReading.timestamp >= start_date)
    
    if end_date:
        query = query.filter(EnergyReading.timestamp <= end_date)
    
    readings = query.order_by(EnergyReading.timestamp.desc()).limit(limit).all()
    
    return readings


@router.get("/{meter_id}/statistics")
async def get_meter_statistics(
    meter_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: Session = Depends(get_db)
):
    """Get statistical analysis for a meter"""
    
    # Verify meter exists
    meter = db.query(SmartMeter).filter(SmartMeter.meter_id == meter_id).first()
    if not meter:
        raise HTTPException(status_code=404, detail="Meter not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get statistics
    stats = db.query(
        func.count(EnergyReading.id).label("reading_count"),
        func.sum(EnergyReading.active_energy).label("total_energy"),
        func.avg(EnergyReading.active_power).label("avg_power"),
        func.min(EnergyReading.active_power).label("min_power"),
        func.max(EnergyReading.active_power).label("max_power"),
        func.avg(EnergyReading.voltage_l1).label("avg_voltage"),
        func.avg(EnergyReading.power_factor).label("avg_power_factor")
    ).filter(
        EnergyReading.meter_id == meter_id,
        EnergyReading.timestamp >= start_date
    ).first()
    
    return {
        "meter_id": meter_id,
        "analysis_period_days": days,
        "reading_count": stats.reading_count or 0,
        "total_energy_kwh": float(stats.total_energy or 0),
        "average_power_kw": float(stats.avg_power or 0),
        "minimum_power_kw": float(stats.min_power or 0),
        "maximum_power_kw": float(stats.max_power or 0),
        "average_voltage_v": float(stats.avg_voltage or 0),
        "average_power_factor": float(stats.avg_power_factor or 0)
    }
