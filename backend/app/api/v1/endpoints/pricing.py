"""
Dynamic pricing API endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.services.pricing_service import PricingService
from app.models.pricing import DynamicPricing, EnergyPrice
from app.schemas.pricing import (
    CurrentPriceResponse,
    PriceForecastResponse,
    PricingOptimizationResponse
)
from app.core.security import get_current_user

router = APIRouter()
pricing_service = PricingService()


@router.get("/current", response_model=CurrentPriceResponse)
async def get_current_price(
    meter_type: str = Query("residential", regex="^(residential|commercial|industrial)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current energy price"""
    try:
        price_data = pricing_service.get_current_price(meter_type)
        return CurrentPriceResponse(**price_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting current price: {str(e)}")


@router.get("/forecast", response_model=List[PriceForecastResponse])
async def get_price_forecast(
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours to forecast"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get price forecast for next N hours"""
    try:
        forecast_data = pricing_service.get_price_forecast(hours_ahead)
        return [PriceForecastResponse(**item) for item in forecast_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting price forecast: {str(e)}")


@router.get("/optimization", response_model=List[PricingOptimizationResponse])
async def get_pricing_optimization(
    start_date: Optional[datetime] = Query(None, description="Start date for optimization data"),
    end_date: Optional[datetime] = Query(None, description="End date for optimization data"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pricing optimization results"""
    
    query = db.query(DynamicPricing)
    
    if start_date:
        query = query.filter(DynamicPricing.target_timestamp >= start_date)
    
    if end_date:
        query = query.filter(DynamicPricing.target_timestamp <= end_date)
    
    optimizations = query.order_by(DynamicPricing.target_timestamp.desc()).limit(limit).all()
    
    return [
        PricingOptimizationResponse(
            target_timestamp=opt.target_timestamp,
            optimized_price_kwh=opt.optimized_price_kwh,
            adjustment_factor=opt.price_adjustment_factor,
            predicted_demand_kw=opt.predicted_demand_kw,
            predicted_supply_kw=opt.predicted_supply_kw,
            renewable_generation_kw=opt.renewable_generation_kw,
            optimization_algorithm=opt.optimization_algorithm,
            optimization_confidence=opt.optimization_confidence,
            created_at=opt.created_at
        )
        for opt in optimizations
    ]


@router.post("/optimize")
async def trigger_pricing_optimization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger pricing optimization"""
    try:
        pricing_service.optimize_pricing()
        return {"message": "Pricing optimization triggered successfully", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering optimization: {str(e)}")


@router.get("/history")
async def get_pricing_history(
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    meter_type: str = Query("residential", regex="^(residential|commercial|industrial)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical pricing data"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    prices = db.query(EnergyPrice).filter(
        EnergyPrice.timestamp >= start_date
    ).order_by(EnergyPrice.timestamp.desc()).all()
    
    # Apply meter type multipliers
    type_multipliers = {
        "residential": 1.0,
        "commercial": 0.95,
        "industrial": 0.90
    }
    multiplier = type_multipliers.get(meter_type, 1.0)
    
    return [
        {
            "timestamp": price.timestamp,
            "base_price_kwh": price.base_price_kwh * multiplier,
            "peak_price_kwh": price.peak_price_kwh * multiplier,
            "off_peak_price_kwh": price.off_peak_price_kwh * multiplier,
            "season": price.season,
            "wholesale_price": price.wholesale_price
        }
        for price in prices
    ]


@router.get("/tiers")
async def get_pricing_tiers(
    current_user: User = Depends(get_current_user)
):
    """Get current pricing tier information"""
    current_hour = datetime.utcnow().hour
    
    tiers = {
        "peak": {
            "hours": "17:00 - 21:00",
            "multiplier": 1.5,
            "description": "High demand period with premium pricing"
        },
        "off_peak": {
            "hours": "22:00 - 06:00",
            "multiplier": 0.8,
            "description": "Low demand period with discounted pricing"
        },
        "standard": {
            "hours": "06:00 - 17:00, 21:00 - 22:00",
            "multiplier": 1.0,
            "description": "Normal pricing period"
        }
    }
    
    # Determine current tier
    if 17 <= current_hour <= 21:
        current_tier = "peak"
    elif 22 <= current_hour <= 6:
        current_tier = "off_peak"
    else:
        current_tier = "standard"
    
    return {
        "current_tier": current_tier,
        "current_hour": current_hour,
        "tiers": tiers
    }


@router.get("/market-conditions")
async def get_market_conditions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current market conditions affecting pricing"""
    
    # This would typically fetch from market data APIs
    # For now, return simulated data
    
    return {
        "timestamp": datetime.utcnow(),
        "wholesale_price_mwh": 45.50,
        "demand_mw": 1250.5,
        "supply_mw": 1320.8,
        "renewable_percentage": 25.6,
        "grid_frequency_hz": 50.02,
        "transmission_congestion": "low",
        "weather_impact": "moderate",
        "market_status": "normal"
    }
