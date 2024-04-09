"""
Grid Monitoring Service
Monitors grid health, stability, and performance
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.smart_meter import EnergyReading
from app.models.renewable_energy import RenewableEnergyGeneration
from app.models.pricing import MarketData

logger = logging.getLogger(__name__)


class GridMonitoringService:
    """Service for monitoring grid health and stability"""
    
    def __init__(self):
        self.frequency_threshold = 0.1  # Hz deviation threshold
        self.voltage_threshold = 0.05   # 5% voltage deviation
        self.load_threshold = 0.95      # 95% load threshold
    
    def check_grid_health(self) -> Dict:
        """Perform comprehensive grid health check"""
        try:
            db = SessionLocal()
            
            # Get current grid metrics
            frequency_status = self._check_frequency_stability(db)
            voltage_status = self._check_voltage_stability(db)
            load_status = self._check_load_balance(db)
            renewable_status = self._check_renewable_integration(db)
            
            # Calculate overall health score
            health_score = self._calculate_health_score(
                frequency_status, voltage_status, load_status, renewable_status
            )
            
            # Determine overall status
            if health_score >= 0.9:
                overall_status = "excellent"
            elif health_score >= 0.8:
                overall_status = "good"
            elif health_score >= 0.7:
                overall_status = "fair"
            elif health_score >= 0.6:
                overall_status = "poor"
            else:
                overall_status = "critical"
            
            # Generate alerts if needed
            alerts = self._generate_alerts(
                frequency_status, voltage_status, load_status, renewable_status
            )
            
            db.close()
            
            health_report = {
                "timestamp": datetime.utcnow(),
                "overall_status": overall_status,
                "health_score": round(health_score, 3),
                "metrics": {
                    "frequency": frequency_status,
                    "voltage": voltage_status,
                    "load": load_status,
                    "renewable": renewable_status
                },
                "alerts": alerts
            }
            
            # Log critical issues
            if overall_status in ["poor", "critical"]:
                logger.warning(f"Grid health critical: {overall_status}, score: {health_score}")
            
            return health_report
            
        except Exception as e:
            logger.error(f"Error checking grid health: {e}")
            raise
    
    def _check_frequency_stability(self, db: Session) -> Dict:
        """Check grid frequency stability"""
        try:
            # Get recent frequency data (last hour)
            recent_time = datetime.utcnow() - timedelta(hours=1)
            
            # Simulate frequency data (in real implementation, get from grid sensors)
            current_frequency = 50.02  # Hz
            target_frequency = 50.0
            
            deviation = abs(current_frequency - target_frequency)
            
            if deviation <= 0.05:
                status = "stable"
                score = 1.0
            elif deviation <= 0.1:
                status = "minor_deviation"
                score = 0.8
            elif deviation <= 0.2:
                status = "moderate_deviation"
                score = 0.6
            else:
                status = "unstable"
                score = 0.3
            
            return {
                "current_frequency": current_frequency,
                "target_frequency": target_frequency,
                "deviation": round(deviation, 3),
                "status": status,
                "score": score
            }
            
        except Exception as e:
            logger.error(f"Error checking frequency stability: {e}")
            return {"status": "error", "score": 0.0}
    
    def _check_voltage_stability(self, db: Session) -> Dict:
        """Check voltage stability across the grid"""
        try:
            # Get recent voltage readings from smart meters
            recent_time = datetime.utcnow() - timedelta(minutes=30)
            
            voltage_readings = db.query(
                func.avg(EnergyReading.voltage_l1).label("avg_voltage"),
                func.min(EnergyReading.voltage_l1).label("min_voltage"),
                func.max(EnergyReading.voltage_l1).label("max_voltage"),
                func.count(EnergyReading.id).label("reading_count")
            ).filter(
                EnergyReading.timestamp >= recent_time,
                EnergyReading.voltage_l1.isnot(None)
            ).first()
            
            if not voltage_readings or not voltage_readings.avg_voltage:
                return {"status": "no_data", "score": 0.5}
            
            avg_voltage = float(voltage_readings.avg_voltage)
            min_voltage = float(voltage_readings.min_voltage)
            max_voltage = float(voltage_readings.max_voltage)
            
            # Standard voltage is 230V
            target_voltage = 230.0
            voltage_range = max_voltage - min_voltage
            avg_deviation = abs(avg_voltage - target_voltage) / target_voltage
            
            if avg_deviation <= 0.02 and voltage_range <= 10:  # 2% deviation, 10V range
                status = "stable"
                score = 1.0
            elif avg_deviation <= 0.05 and voltage_range <= 20:  # 5% deviation, 20V range
                status = "minor_variation"
                score = 0.8
            elif avg_deviation <= 0.1 and voltage_range <= 30:   # 10% deviation, 30V range
                status = "moderate_variation"
                score = 0.6
            else:
                status = "unstable"
                score = 0.3
            
            return {
                "average_voltage": round(avg_voltage, 1),
                "min_voltage": round(min_voltage, 1),
                "max_voltage": round(max_voltage, 1),
                "voltage_range": round(voltage_range, 1),
                "deviation_percent": round(avg_deviation * 100, 2),
                "status": status,
                "score": score,
                "reading_count": voltage_readings.reading_count
            }
            
        except Exception as e:
            logger.error(f"Error checking voltage stability: {e}")
            return {"status": "error", "score": 0.0}
    
    def _check_load_balance(self, db: Session) -> Dict:
        """Check grid load balance and capacity"""
        try:
            # Get current total demand
            recent_time = datetime.utcnow() - timedelta(minutes=15)
            
            total_demand = db.query(
                func.sum(EnergyReading.active_power).label("total_power")
            ).filter(
                EnergyReading.timestamp >= recent_time,
                EnergyReading.active_power.isnot(None)
            ).scalar()
            
            if not total_demand:
                total_demand = 0
            
            # Simulate grid capacity (in real implementation, get from grid operator)
            grid_capacity = 2000.0  # kW
            load_factor = total_demand / grid_capacity if grid_capacity > 0 else 0
            
            if load_factor <= 0.7:
                status = "normal"
                score = 1.0
            elif load_factor <= 0.85:
                status = "moderate"
                score = 0.8
            elif load_factor <= 0.95:
                status = "high"
                score = 0.6
            else:
                status = "critical"
                score = 0.2
            
            return {
                "total_demand_kw": round(float(total_demand), 1),
                "grid_capacity_kw": grid_capacity,
                "load_factor": round(load_factor, 3),
                "load_factor_percent": round(load_factor * 100, 1),
                "status": status,
                "score": score
            }
            
        except Exception as e:
            logger.error(f"Error checking load balance: {e}")
            return {"status": "error", "score": 0.0}
    
    def _check_renewable_integration(self, db: Session) -> Dict:
        """Check renewable energy integration status"""
        try:
            # Get recent renewable generation
            recent_time = datetime.utcnow() - timedelta(minutes=15)
            
            renewable_generation = db.query(
                func.sum(RenewableEnergyGeneration.power_output_kw).label("total_renewable"),
                func.count(RenewableEnergyGeneration.id).label("source_count")
            ).filter(
                RenewableEnergyGeneration.timestamp >= recent_time
            ).first()
            
            # Get total demand for comparison
            total_demand = db.query(
                func.sum(EnergyReading.active_power).label("total_power")
            ).filter(
                EnergyReading.timestamp >= recent_time,
                EnergyReading.active_power.isnot(None)
            ).scalar()
            
            if not renewable_generation or not renewable_generation.total_renewable:
                renewable_power = 0
                source_count = 0
            else:
                renewable_power = float(renewable_generation.total_renewable)
                source_count = renewable_generation.source_count
            
            if not total_demand:
                total_demand = 0
            
            # Calculate renewable penetration
            renewable_penetration = renewable_power / total_demand if total_demand > 0 else 0
            
            if renewable_penetration >= 0.3:  # 30% renewable
                status = "excellent"
                score = 1.0
            elif renewable_penetration >= 0.2:  # 20% renewable
                status = "good"
                score = 0.8
            elif renewable_penetration >= 0.1:  # 10% renewable
                status = "moderate"
                score = 0.6
            else:
                status = "low"
                score = 0.4
            
            return {
                "renewable_power_kw": round(renewable_power, 1),
                "total_demand_kw": round(float(total_demand), 1),
                "renewable_penetration": round(renewable_penetration, 3),
                "renewable_penetration_percent": round(renewable_penetration * 100, 1),
                "active_sources": source_count,
                "status": status,
                "score": score
            }
            
        except Exception as e:
            logger.error(f"Error checking renewable integration: {e}")
            return {"status": "error", "score": 0.0}
    
    def _calculate_health_score(self, frequency: Dict, voltage: Dict, load: Dict, renewable: Dict) -> float:
        """Calculate overall grid health score"""
        weights = {
            "frequency": 0.3,
            "voltage": 0.3,
            "load": 0.25,
            "renewable": 0.15
        }
        
        score = (
            frequency.get("score", 0) * weights["frequency"] +
            voltage.get("score", 0) * weights["voltage"] +
            load.get("score", 0) * weights["load"] +
            renewable.get("score", 0) * weights["renewable"]
        )
        
        return score
    
    def _generate_alerts(self, frequency: Dict, voltage: Dict, load: Dict, renewable: Dict) -> List[Dict]:
        """Generate alerts based on grid conditions"""
        alerts = []
        
        # Frequency alerts
        if frequency.get("status") == "unstable":
            alerts.append({
                "type": "critical",
                "category": "frequency",
                "message": f"Grid frequency unstable: {frequency.get('current_frequency', 0)}Hz",
                "timestamp": datetime.utcnow()
            })
        elif frequency.get("status") == "moderate_deviation":
            alerts.append({
                "type": "warning",
                "category": "frequency",
                "message": f"Grid frequency deviation detected: {frequency.get('deviation', 0)}Hz",
                "timestamp": datetime.utcnow()
            })
        
        # Voltage alerts
        if voltage.get("status") == "unstable":
            alerts.append({
                "type": "critical",
                "category": "voltage",
                "message": f"Voltage instability detected: {voltage.get('deviation_percent', 0)}% deviation",
                "timestamp": datetime.utcnow()
            })
        
        # Load alerts
        if load.get("status") == "critical":
            alerts.append({
                "type": "critical",
                "category": "load",
                "message": f"Grid overload: {load.get('load_factor_percent', 0)}% capacity",
                "timestamp": datetime.utcnow()
            })
        elif load.get("status") == "high":
            alerts.append({
                "type": "warning",
                "category": "load",
                "message": f"High grid load: {load.get('load_factor_percent', 0)}% capacity",
                "timestamp": datetime.utcnow()
            })
        
        # Renewable alerts
        if renewable.get("renewable_penetration_percent", 0) < 5:
            alerts.append({
                "type": "info",
                "category": "renewable",
                "message": f"Low renewable penetration: {renewable.get('renewable_penetration_percent', 0)}%",
                "timestamp": datetime.utcnow()
            })
        
        return alerts
    
    def get_grid_history(self, hours: int = 24) -> Dict:
        """Get grid health history"""
        try:
            # In a real implementation, this would query historical grid data
            # For now, return simulated historical data
            
            history = []
            current_time = datetime.utcnow()
            
            for i in range(hours):
                timestamp = current_time - timedelta(hours=i)
                
                # Simulate varying grid conditions
                base_score = 0.85 + (i % 5) * 0.03
                
                history.append({
                    "timestamp": timestamp,
                    "health_score": round(base_score, 3),
                    "status": "good" if base_score >= 0.8 else "fair"
                })
            
            return {
                "period_hours": hours,
                "history": list(reversed(history)),
                "average_score": round(sum(h["health_score"] for h in history) / len(history), 3)
            }
            
        except Exception as e:
            logger.error(f"Error getting grid history: {e}")
            raise
