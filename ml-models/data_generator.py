"""
Smart Grid Data Generator
Generates realistic smart meter and renewable energy data for testing
"""

import random
import json
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List
import paho.mqtt.client as mqtt
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SmartGridDataGenerator:
    """Generates realistic smart grid data"""
    
    def __init__(self, mqtt_broker: str = "localhost", mqtt_port: int = 1883):
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.client = None
        
        # Smart meter configurations
        self.smart_meters = [
            {"id": "SM001", "type": "residential", "base_consumption": 15, "location": [40.7128, -74.0060]},
            {"id": "SM002", "type": "residential", "base_consumption": 12, "location": [40.7130, -74.0058]},
            {"id": "SM003", "type": "commercial", "base_consumption": 85, "location": [40.7589, -73.9851]},
            {"id": "SM004", "type": "industrial", "base_consumption": 250, "location": [40.6892, -74.0445]},
            {"id": "SM005", "type": "residential", "base_consumption": 18, "location": [40.7505, -73.9934]},
        ]
        
        # Solar panel configurations
        self.solar_panels = [
            {"id": "SP001", "capacity": 10.5, "location": [40.7128, -74.0060]},
            {"id": "SP002", "capacity": 25.0, "location": [40.7589, -73.9851]},
            {"id": "SP003", "capacity": 50.0, "location": [40.7505, -73.9934]},
        ]
        
        # Wind turbine configurations
        self.wind_turbines = [
            {"id": "WT001", "capacity": 2000.0, "location": [40.5000, -74.2000]},
            {"id": "WT002", "capacity": 2000.0, "location": [40.5010, -74.2010]},
            {"id": "WT003", "capacity": 1500.0, "location": [40.8000, -74.1000]},
        ]
    
    def connect_mqtt(self):
        """Connect to MQTT broker"""
        try:
            self.client = mqtt.Client(client_id="data_generator")
            self.client.connect(self.mqtt_broker, self.mqtt_port, 60)
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.mqtt_broker}:{self.mqtt_port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect_mqtt(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("Disconnected from MQTT broker")
    
    def generate_smart_meter_data(self, meter: Dict) -> Dict:
        """Generate realistic smart meter data"""
        now = datetime.utcnow()
        hour = now.hour
        day_of_week = now.weekday()
        
        # Base consumption with time-of-day and day-of-week patterns
        base = meter["base_consumption"]
        
        # Time of day factor
        if meter["type"] == "residential":
            if 6 <= hour <= 9 or 17 <= hour <= 22:  # Morning and evening peaks
                time_factor = 1.4
            elif 10 <= hour <= 16:  # Daytime
                time_factor = 0.7
            else:  # Night
                time_factor = 0.5
        elif meter["type"] == "commercial":
            if 8 <= hour <= 18:  # Business hours
                time_factor = 1.2
            else:
                time_factor = 0.3
        else:  # Industrial
            time_factor = 1.0 + 0.2 * math.sin(2 * math.pi * hour / 24)
        
        # Day of week factor
        if day_of_week < 5:  # Weekday
            day_factor = 1.0
        else:  # Weekend
            day_factor = 0.8 if meter["type"] == "commercial" else 1.1
        
        # Random variation
        random_factor = random.uniform(0.85, 1.15)
        
        # Calculate power
        active_power = base * time_factor * day_factor * random_factor
        
        # Calculate other electrical parameters
        voltage_l1 = random.uniform(225, 235)
        current_l1 = active_power * 1000 / voltage_l1  # Convert kW to W
        power_factor = random.uniform(0.92, 0.98)
        frequency = random.uniform(49.8, 50.2)
        
        # Energy is power * time interval (assuming 15-minute intervals)
        active_energy = active_power * 0.25  # kWh for 15 minutes
        
        return {
            "meter_id": meter["id"],
            "timestamp": now.isoformat(),
            "active_energy": round(active_energy, 3),
            "reactive_energy": round(active_energy * 0.1, 3),
            "apparent_energy": round(active_energy * 1.05, 3),
            "active_power": round(active_power, 2),
            "reactive_power": round(active_power * 0.1, 2),
            "power_factor": round(power_factor, 3),
            "voltage_l1": round(voltage_l1, 1),
            "voltage_l2": round(voltage_l1 + random.uniform(-2, 2), 1),
            "voltage_l3": round(voltage_l1 + random.uniform(-2, 2), 1),
            "current_l1": round(current_l1, 2),
            "current_l2": round(current_l1 + random.uniform(-1, 1), 2),
            "current_l3": round(current_l1 + random.uniform(-1, 1), 2),
            "frequency": round(frequency, 2),
            "quality_flag": "good"
        }
    
    def generate_solar_data(self, panel: Dict) -> Dict:
        """Generate realistic solar panel data"""
        now = datetime.utcnow()
        hour = now.hour
        
        # Solar irradiance based on time of day
        if 6 <= hour <= 18:
            # Simplified solar curve
            solar_angle = abs(12 - hour) / 6  # 0 at noon, 1 at 6am/6pm
            base_irradiance = 1000 * (1 - solar_angle * 0.8)
            
            # Add weather variation
            cloud_factor = random.uniform(0.7, 1.0)
            irradiance = base_irradiance * cloud_factor
        else:
            irradiance = 0
        
        # Temperature variation
        temperature = 20 + 15 * math.sin(2 * math.pi * (hour - 6) / 24) + random.uniform(-3, 3)
        
        # Power output calculation
        efficiency = 0.20 * (1 - 0.004 * max(0, temperature - 25))  # Temperature derating
        panel_area = panel["capacity"] / 0.20  # Assuming 20% base efficiency
        power_output = (irradiance / 1000) * panel_area * efficiency
        
        # Capacity factor
        capacity_factor = power_output / panel["capacity"] if panel["capacity"] > 0 else 0
        
        return {
            "panel_id": panel["id"],
            "timestamp": now.isoformat(),
            "power_output_kw": round(max(0, power_output), 2),
            "energy_generated_kwh": round(max(0, power_output * 0.25), 3),  # 15-minute interval
            "irradiance_wm2": round(max(0, irradiance), 1),
            "temperature_c": round(temperature, 1),
            "capacity_factor": round(max(0, capacity_factor), 3),
            "efficiency": round(efficiency, 3)
        }
    
    def generate_wind_data(self, turbine: Dict) -> Dict:
        """Generate realistic wind turbine data"""
        now = datetime.utcnow()
        
        # Wind speed variation (simplified model)
        base_wind_speed = 8 + 4 * math.sin(2 * math.pi * now.hour / 24)
        wind_speed = max(0, base_wind_speed + random.uniform(-3, 3))
        
        # Wind direction
        wind_direction = random.uniform(0, 360)
        
        # Temperature
        temperature = 15 + 10 * math.sin(2 * math.pi * now.hour / 24) + random.uniform(-2, 2)
        
        # Power curve calculation (simplified)
        cut_in_speed = 3.0
        cut_out_speed = 25.0
        rated_speed = 12.0
        
        if wind_speed < cut_in_speed or wind_speed > cut_out_speed:
            power_output = 0
        elif wind_speed >= rated_speed:
            power_output = turbine["capacity"]
        else:
            # Linear interpolation between cut-in and rated
            power_ratio = (wind_speed - cut_in_speed) / (rated_speed - cut_in_speed)
            power_output = turbine["capacity"] * power_ratio
        
        # Add some efficiency losses
        power_output *= random.uniform(0.95, 1.0)
        
        # Capacity factor
        capacity_factor = power_output / turbine["capacity"] if turbine["capacity"] > 0 else 0
        
        return {
            "turbine_id": turbine["id"],
            "timestamp": now.isoformat(),
            "power_output_kw": round(max(0, power_output), 1),
            "energy_generated_kwh": round(max(0, power_output * 0.25), 3),  # 15-minute interval
            "wind_speed_ms": round(wind_speed, 1),
            "wind_direction_deg": round(wind_direction, 1),
            "temperature_c": round(temperature, 1),
            "capacity_factor": round(max(0, capacity_factor), 3),
            "efficiency": round(random.uniform(0.92, 0.98), 3)
        }
    
    def generate_grid_status(self) -> Dict:
        """Generate grid status data"""
        now = datetime.utcnow()
        
        # Grid frequency (should be close to 50 Hz)
        frequency = 50.0 + random.uniform(-0.1, 0.1)
        
        # Voltage stability (0-1 scale)
        voltage_stability = random.uniform(0.95, 1.0)
        
        # Total demand and supply (simplified)
        hour = now.hour
        base_demand = 1000 + 200 * math.sin(2 * math.pi * (hour - 6) / 24)
        total_demand = base_demand + random.uniform(-50, 50)
        total_supply = total_demand + random.uniform(-20, 30)
        
        return {
            "timestamp": now.isoformat(),
            "frequency_hz": round(frequency, 3),
            "voltage_stability": round(voltage_stability, 3),
            "total_demand_mw": round(total_demand, 1),
            "total_supply_mw": round(total_supply, 1),
            "grid_status": "normal" if abs(frequency - 50.0) < 0.05 else "warning"
        }
    
    def publish_data(self):
        """Publish all data types to MQTT"""
        if not self.client:
            logger.error("MQTT client not connected")
            return
        
        # Generate and publish smart meter data
        for meter in self.smart_meters:
            data = self.generate_smart_meter_data(meter)
            topic = f"smartgrid/meters/{meter['id']}/data"
            self.client.publish(topic, json.dumps(data))
            logger.info(f"Published meter data: {meter['id']}")
        
        # Generate and publish solar data
        for panel in self.solar_panels:
            data = self.generate_solar_data(panel)
            topic = f"smartgrid/solar/{panel['id']}/data"
            self.client.publish(topic, json.dumps(data))
            logger.info(f"Published solar data: {panel['id']}")
        
        # Generate and publish wind data
        for turbine in self.wind_turbines:
            data = self.generate_wind_data(turbine)
            topic = f"smartgrid/wind/{turbine['id']}/data"
            self.client.publish(topic, json.dumps(data))
            logger.info(f"Published wind data: {turbine['id']}")
        
        # Generate and publish grid status
        grid_data = self.generate_grid_status()
        self.client.publish("smartgrid/grid/status", json.dumps(grid_data))
        logger.info("Published grid status")
    
    def run_continuous(self, interval: int = 900):  # 15 minutes default
        """Run data generation continuously"""
        logger.info(f"Starting continuous data generation (interval: {interval}s)")
        
        if not self.connect_mqtt():
            return
        
        try:
            while True:
                self.publish_data()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Stopping data generation...")
        finally:
            self.disconnect_mqtt()


if __name__ == "__main__":
    import sys

    # Get MQTT port from command line or use default
    mqtt_port = 1885  # Default to Docker mapped port
    if len(sys.argv) > 1:
        try:
            mqtt_port = int(sys.argv[1])
        except ValueError:
            logger.warning(f"Invalid port argument: {sys.argv[1]}, using default 1885")

    logger.info(f"Using MQTT port: {mqtt_port}")
    generator = SmartGridDataGenerator(mqtt_port=mqtt_port)
    generator.run_continuous(interval=60)  # Generate data every minute for testing
