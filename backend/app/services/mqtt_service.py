"""
MQTT Service for Smart Meter Data Aggregation
Handles real-time data collection from IoT devices
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.smart_meter import EnergyReading, SmartMeter
from app.models.renewable_energy import RenewableEnergyGeneration

logger = logging.getLogger(__name__)


class MQTTService:
    """MQTT service for handling smart meter and renewable energy data"""

    def __init__(self):
        self.client = None
        self.is_connected = False
        self.topics = {
            "smart_meters": "smartgrid/meters/+/data",
            "solar_panels": "smartgrid/solar/+/data",
            "wind_turbines": "smartgrid/wind/+/data",
            "grid_status": "smartgrid/grid/status",
            "pricing": "smartgrid/pricing/update"
        }

    async def start(self):
        """Start MQTT service"""
        try:
            # Use the new callback API version for paho-mqtt 2.x
            self.client = mqtt.Client(
                client_id="smartgrid_backend",
                callback_api_version=mqtt.CallbackAPIVersion.VERSION1
            )
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message

            # Set authentication if configured
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

            # Connect to broker
            self.client.connect(
                settings.MQTT_BROKER_HOST,
                settings.MQTT_BROKER_PORT,
                settings.MQTT_KEEPALIVE
            )

            # Start the loop in a separate thread
            self.client.loop_start()

            logger.info(f"MQTT service started, connecting to {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")

        except Exception as e:
            logger.error(f"Failed to start MQTT service: {e}")
            raise

    async def stop(self):
        """Stop MQTT service"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT service stopped")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response"""
        if rc == 0:
            self.is_connected = True
            logger.info("Connected to MQTT broker")

            # Subscribe to all topics
            for topic_name, topic_pattern in self.topics.items():
                client.subscribe(topic_pattern)
                logger.info(f"Subscribed to {topic_name}: {topic_pattern}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects"""
        self.is_connected = False
        logger.warning(f"Disconnected from MQTT broker, return code {rc}")

    def _on_message(self, client, userdata, msg):
        """Callback for when a message is received"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())

            logger.debug(f"Received message on topic {topic}: {payload}")

            # Route message based on topic
            if "meters" in topic:
                self._handle_meter_data(topic, payload)
            elif "solar" in topic:
                self._handle_solar_data(topic, payload)
            elif "wind" in topic:
                self._handle_wind_data(topic, payload)
            elif "grid/status" in topic:
                self._handle_grid_status(payload)
            elif "pricing" in topic:
                self._handle_pricing_update(payload)

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _handle_meter_data(self, topic: str, payload: Dict[str, Any]):
        """Handle smart meter data"""
        try:
            # Extract meter ID from topic: smartgrid/meters/{meter_id}/data
            meter_id = topic.split('/')[2]

            db = SessionLocal()
            try:
                # Verify meter exists
                meter = db.query(SmartMeter).filter(SmartMeter.meter_id == meter_id).first()
                if not meter:
                    logger.warning(f"Unknown meter ID: {meter_id}")
                    return

                # Create energy reading
                reading = EnergyReading(
                    meter_id=meter_id,
                    timestamp=datetime.fromisoformat(payload.get('timestamp', datetime.utcnow().isoformat())),
                    active_energy=payload.get('active_energy'),
                    reactive_energy=payload.get('reactive_energy'),
                    apparent_energy=payload.get('apparent_energy'),
                    active_power=payload.get('active_power'),
                    reactive_power=payload.get('reactive_power'),
                    power_factor=payload.get('power_factor'),
                    voltage_l1=payload.get('voltage_l1'),
                    voltage_l2=payload.get('voltage_l2'),
                    voltage_l3=payload.get('voltage_l3'),
                    current_l1=payload.get('current_l1'),
                    current_l2=payload.get('current_l2'),
                    current_l3=payload.get('current_l3'),
                    frequency=payload.get('frequency'),
                    quality_flag=payload.get('quality_flag', 'good')
                )

                db.add(reading)

                # Update meter last communication
                meter.last_communication = datetime.utcnow()

                db.commit()
                logger.debug(f"Stored energy reading for meter {meter_id}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error handling meter data: {e}")

    def _handle_solar_data(self, topic: str, payload: Dict[str, Any]):
        """Handle solar panel data"""
        try:
            # Extract panel ID from topic: smartgrid/solar/{panel_id}/data
            panel_id = topic.split('/')[2]

            db = SessionLocal()
            try:
                generation = RenewableEnergyGeneration(
                    source_id=panel_id,
                    source_type="solar",
                    timestamp=datetime.fromisoformat(payload.get('timestamp', datetime.utcnow().isoformat())),
                    power_output_kw=payload.get('power_output_kw'),
                    energy_generated_kwh=payload.get('energy_generated_kwh'),
                    irradiance_wm2=payload.get('irradiance_wm2'),
                    temperature_c=payload.get('temperature_c'),
                    capacity_factor=payload.get('capacity_factor'),
                    efficiency=payload.get('efficiency')
                )

                db.add(generation)
                db.commit()
                logger.debug(f"Stored solar generation data for panel {panel_id}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error handling solar data: {e}")

    def _handle_wind_data(self, topic: str, payload: Dict[str, Any]):
        """Handle wind turbine data"""
        try:
            # Extract turbine ID from topic: smartgrid/wind/{turbine_id}/data
            turbine_id = topic.split('/')[2]

            db = SessionLocal()
            try:
                generation = RenewableEnergyGeneration(
                    source_id=turbine_id,
                    source_type="wind",
                    timestamp=datetime.fromisoformat(payload.get('timestamp', datetime.utcnow().isoformat())),
                    power_output_kw=payload.get('power_output_kw'),
                    energy_generated_kwh=payload.get('energy_generated_kwh'),
                    wind_speed_ms=payload.get('wind_speed_ms'),
                    wind_direction_deg=payload.get('wind_direction_deg'),
                    temperature_c=payload.get('temperature_c'),
                    capacity_factor=payload.get('capacity_factor'),
                    efficiency=payload.get('efficiency')
                )

                db.add(generation)
                db.commit()
                logger.debug(f"Stored wind generation data for turbine {turbine_id}")

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Error handling wind data: {e}")

    def _handle_grid_status(self, payload: Dict[str, Any]):
        """Handle grid status updates"""
        try:
            # Log grid status for monitoring
            logger.info(f"Grid status update: {payload}")

            # Here you could store grid status in a dedicated table
            # or trigger alerts based on grid conditions

        except Exception as e:
            logger.error(f"Error handling grid status: {e}")

    def _handle_pricing_update(self, payload: Dict[str, Any]):
        """Handle pricing updates"""
        try:
            # Log pricing updates
            logger.info(f"Pricing update: {payload}")

            # Here you could trigger dynamic pricing recalculation
            # or update pricing models

        except Exception as e:
            logger.error(f"Error handling pricing update: {e}")

    def publish_message(self, topic: str, payload: Dict[str, Any]):
        """Publish a message to MQTT broker"""
        try:
            if self.client and self.is_connected:
                message = json.dumps(payload)
                self.client.publish(topic, message)
                logger.debug(f"Published message to {topic}: {payload}")
            else:
                logger.warning("Cannot publish message: MQTT client not connected")
        except Exception as e:
            logger.error(f"Error publishing message: {e}")

    def publish_pricing_update(self, pricing_data: Dict[str, Any]):
        """Publish pricing update to all subscribers"""
        self.publish_message("smartgrid/pricing/update", pricing_data)

    def publish_grid_alert(self, alert_data: Dict[str, Any]):
        """Publish grid alert"""
        self.publish_message("smartgrid/grid/alert", alert_data)
