"""
Dynamic Pricing Optimization Service
Implements advanced algorithms for optimal energy pricing
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.pricing import EnergyPrice, DynamicPricing, MarketData
from app.models.smart_meter import EnergyReading, EnergyPrediction
from app.models.renewable_energy import RenewableForecast

logger = logging.getLogger(__name__)


class PricingService:
    """Service for dynamic pricing optimization"""
    
    def __init__(self):
        self.base_price = settings.BASE_ENERGY_PRICE
        self.peak_multiplier = settings.PEAK_HOUR_MULTIPLIER
        self.off_peak_multiplier = settings.OFF_PEAK_MULTIPLIER
    
    def optimize_pricing(self):
        """Run dynamic pricing optimization"""
        try:
            db = SessionLocal()
            
            # Get current market conditions
            market_data = self._get_current_market_data(db)
            
            # Get demand predictions for next 24 hours
            demand_predictions = self._get_demand_predictions(db)
            
            # Get renewable energy forecasts
            renewable_forecasts = self._get_renewable_forecasts(db)
            
            # Calculate optimal pricing for each hour
            optimized_prices = []
            
            for hour_offset in range(24):
                target_time = datetime.utcnow() + timedelta(hours=hour_offset)
                
                # Get predicted demand and supply for this hour
                predicted_demand = self._get_predicted_demand_for_hour(demand_predictions, target_time)
                predicted_renewable = self._get_predicted_renewable_for_hour(renewable_forecasts, target_time)
                
                # Calculate optimal price
                optimal_price = self._calculate_optimal_price(
                    target_time=target_time,
                    predicted_demand=predicted_demand,
                    predicted_renewable=predicted_renewable,
                    market_data=market_data
                )
                
                optimized_prices.append(optimal_price)
            
            # Store optimization results
            self._store_pricing_results(db, optimized_prices)
            
            db.close()
            logger.info("Dynamic pricing optimization completed")
            
        except Exception as e:
            logger.error(f"Error in pricing optimization: {e}")
    
    def _get_current_market_data(self, db: Session) -> Optional[Dict]:
        """Get current market conditions"""
        try:
            # Get latest market data
            latest_market = db.query(MarketData).order_by(MarketData.timestamp.desc()).first()
            
            if latest_market:
                return {
                    "wholesale_price": latest_market.real_time_price or self.base_price,
                    "total_demand": latest_market.total_demand_mw or 1000,
                    "total_supply": latest_market.total_supply_mw or 1100,
                    "renewable_supply": latest_market.renewable_supply_mw or 200,
                    "grid_frequency": latest_market.frequency_hz or 50.0
                }
            else:
                # Default market conditions
                return {
                    "wholesale_price": self.base_price,
                    "total_demand": 1000,
                    "total_supply": 1100,
                    "renewable_supply": 200,
                    "grid_frequency": 50.0
                }
                
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
    
    def _get_demand_predictions(self, db: Session) -> List[Dict]:
        """Get energy demand predictions for next 24 hours"""
        try:
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(hours=24)
            
            predictions = db.query(EnergyPrediction).filter(
                EnergyPrediction.target_timestamp >= start_time,
                EnergyPrediction.target_timestamp <= end_time
            ).all()
            
            return [
                {
                    "timestamp": pred.target_timestamp,
                    "predicted_consumption": pred.predicted_consumption,
                    "confidence_lower": pred.confidence_interval_lower,
                    "confidence_upper": pred.confidence_interval_upper
                }
                for pred in predictions
            ]
            
        except Exception as e:
            logger.error(f"Error getting demand predictions: {e}")
            return []
    
    def _get_renewable_forecasts(self, db: Session) -> List[Dict]:
        """Get renewable energy forecasts for next 24 hours"""
        try:
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(hours=24)
            
            forecasts = db.query(RenewableForecast).filter(
                RenewableForecast.target_timestamp >= start_time,
                RenewableForecast.target_timestamp <= end_time
            ).all()
            
            return [
                {
                    "timestamp": forecast.target_timestamp,
                    "source_type": forecast.source_type,
                    "predicted_power": forecast.predicted_power_kw,
                    "predicted_energy": forecast.predicted_energy_kwh
                }
                for forecast in forecasts
            ]
            
        except Exception as e:
            logger.error(f"Error getting renewable forecasts: {e}")
            return []
    
    def _get_predicted_demand_for_hour(self, predictions: List[Dict], target_time: datetime) -> float:
        """Get predicted demand for a specific hour"""
        # Find prediction closest to target time
        closest_prediction = None
        min_time_diff = float('inf')
        
        for pred in predictions:
            time_diff = abs((pred["timestamp"] - target_time).total_seconds())
            if time_diff < min_time_diff:
                min_time_diff = time_diff
                closest_prediction = pred
        
        if closest_prediction:
            return closest_prediction["predicted_consumption"]
        else:
            # Default demand based on time of day
            hour = target_time.hour
            if 17 <= hour <= 21:  # Peak hours
                return 1200  # kW
            elif 22 <= hour <= 6:  # Off-peak hours
                return 600   # kW
            else:  # Normal hours
                return 900   # kW
    
    def _get_predicted_renewable_for_hour(self, forecasts: List[Dict], target_time: datetime) -> float:
        """Get predicted renewable generation for a specific hour"""
        total_renewable = 0
        
        for forecast in forecasts:
            time_diff = abs((forecast["timestamp"] - target_time).total_seconds())
            if time_diff <= 1800:  # Within 30 minutes
                total_renewable += forecast["predicted_power"]
        
        return total_renewable
    
    def _calculate_optimal_price(self, target_time: datetime, predicted_demand: float, 
                               predicted_renewable: float, market_data: Dict) -> Dict:
        """Calculate optimal price using supply-demand optimization"""
        try:
            # Base price from market conditions
            base_price = market_data["wholesale_price"]
            
            # Supply-demand ratio
            total_supply = market_data["total_supply"] + predicted_renewable
            supply_demand_ratio = total_supply / max(predicted_demand, 1)
            
            # Price adjustment based on supply-demand
            if supply_demand_ratio > 1.2:  # Oversupply
                supply_adjustment = 0.8
            elif supply_demand_ratio < 0.9:  # Undersupply
                supply_adjustment = 1.3
            else:  # Balanced
                supply_adjustment = 1.0
            
            # Time-of-use adjustment
            hour = target_time.hour
            if 17 <= hour <= 21:  # Peak hours
                time_adjustment = self.peak_multiplier
            elif 22 <= hour <= 6:  # Off-peak hours
                time_adjustment = self.off_peak_multiplier
            else:  # Normal hours
                time_adjustment = 1.0
            
            # Renewable energy bonus (lower prices when more renewable)
            renewable_ratio = predicted_renewable / max(predicted_demand, 1)
            renewable_adjustment = max(0.7, 1 - (renewable_ratio * 0.3))
            
            # Grid stability factor
            frequency_deviation = abs(market_data["grid_frequency"] - 50.0)
            stability_adjustment = 1 + (frequency_deviation * 0.02)
            
            # Calculate final optimized price
            optimized_price = (base_price * 
                             supply_adjustment * 
                             time_adjustment * 
                             renewable_adjustment * 
                             stability_adjustment)
            
            # Ensure price is within reasonable bounds
            min_price = base_price * 0.5
            max_price = base_price * 2.0
            optimized_price = max(min_price, min(max_price, optimized_price))
            
            # Calculate adjustment factor
            adjustment_factor = optimized_price / base_price
            
            return {
                "target_timestamp": target_time,
                "optimized_price": round(optimized_price, 4),
                "adjustment_factor": round(adjustment_factor, 3),
                "predicted_demand": predicted_demand,
                "predicted_supply": total_supply,
                "renewable_generation": predicted_renewable,
                "supply_demand_ratio": round(supply_demand_ratio, 3),
                "optimization_factors": {
                    "supply_adjustment": round(supply_adjustment, 3),
                    "time_adjustment": round(time_adjustment, 3),
                    "renewable_adjustment": round(renewable_adjustment, 3),
                    "stability_adjustment": round(stability_adjustment, 3)
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating optimal price: {e}")
            return {
                "target_timestamp": target_time,
                "optimized_price": base_price,
                "adjustment_factor": 1.0,
                "predicted_demand": predicted_demand,
                "predicted_supply": 0,
                "renewable_generation": predicted_renewable
            }
    
    def _store_pricing_results(self, db: Session, optimized_prices: List[Dict]):
        """Store pricing optimization results"""
        try:
            optimization_timestamp = datetime.utcnow()
            
            for price_data in optimized_prices:
                pricing_record = DynamicPricing(
                    optimization_timestamp=optimization_timestamp,
                    target_timestamp=price_data["target_timestamp"],
                    optimized_price_kwh=price_data["optimized_price"],
                    price_adjustment_factor=price_data["adjustment_factor"],
                    predicted_demand_kw=price_data["predicted_demand"],
                    predicted_supply_kw=price_data["predicted_supply"],
                    renewable_generation_kw=price_data["renewable_generation"],
                    optimization_algorithm="supply_demand_optimization",
                    optimization_confidence=0.85
                )
                
                db.add(pricing_record)
            
            db.commit()
            logger.info(f"Stored {len(optimized_prices)} pricing optimization results")
            
        except Exception as e:
            logger.error(f"Error storing pricing results: {e}")
            db.rollback()
    
    def get_current_price(self, meter_type: str = "residential") -> Dict:
        """Get current energy price for a meter type"""
        try:
            db = SessionLocal()
            
            # Get latest pricing optimization
            latest_pricing = db.query(DynamicPricing).filter(
                DynamicPricing.target_timestamp >= datetime.utcnow() - timedelta(hours=1),
                DynamicPricing.target_timestamp <= datetime.utcnow() + timedelta(hours=1)
            ).order_by(DynamicPricing.target_timestamp.asc()).first()
            
            if latest_pricing:
                current_price = latest_pricing.optimized_price_kwh
            else:
                # Fallback to base pricing
                current_hour = datetime.utcnow().hour
                if 17 <= current_hour <= 21:  # Peak hours
                    current_price = self.base_price * self.peak_multiplier
                elif 22 <= current_hour <= 6:  # Off-peak hours
                    current_price = self.base_price * self.off_peak_multiplier
                else:
                    current_price = self.base_price
            
            # Apply meter type multiplier
            type_multipliers = {
                "residential": 1.0,
                "commercial": 0.95,
                "industrial": 0.90
            }
            
            final_price = current_price * type_multipliers.get(meter_type, 1.0)
            
            db.close()
            
            return {
                "price_per_kwh": round(final_price, 4),
                "meter_type": meter_type,
                "timestamp": datetime.utcnow(),
                "pricing_tier": self._get_current_pricing_tier()
            }
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return {
                "price_per_kwh": self.base_price,
                "meter_type": meter_type,
                "timestamp": datetime.utcnow(),
                "pricing_tier": "standard"
            }
    
    def _get_current_pricing_tier(self) -> str:
        """Get current pricing tier based on time"""
        current_hour = datetime.utcnow().hour
        if 17 <= current_hour <= 21:
            return "peak"
        elif 22 <= current_hour <= 6:
            return "off_peak"
        else:
            return "standard"
    
    def get_price_forecast(self, hours_ahead: int = 24) -> List[Dict]:
        """Get price forecast for next N hours"""
        try:
            db = SessionLocal()
            
            start_time = datetime.utcnow()
            end_time = start_time + timedelta(hours=hours_ahead)
            
            forecasts = db.query(DynamicPricing).filter(
                DynamicPricing.target_timestamp >= start_time,
                DynamicPricing.target_timestamp <= end_time
            ).order_by(DynamicPricing.target_timestamp.asc()).all()
            
            price_forecast = []
            for forecast in forecasts:
                price_forecast.append({
                    "timestamp": forecast.target_timestamp,
                    "price_per_kwh": forecast.optimized_price_kwh,
                    "adjustment_factor": forecast.price_adjustment_factor,
                    "predicted_demand": forecast.predicted_demand_kw,
                    "renewable_generation": forecast.renewable_generation_kw
                })
            
            db.close()
            return price_forecast
            
        except Exception as e:
            logger.error(f"Error getting price forecast: {e}")
            return []
