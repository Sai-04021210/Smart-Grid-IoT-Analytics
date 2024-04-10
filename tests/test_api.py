"""
API Tests for Smart Grid IoT Analytics
Comprehensive test suite for all API endpoints
"""

import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, Base, engine
from app.models.smart_meter import SmartMeter, EnergyReading

# Test client
client = TestClient(app)


class TestEnergyAPI:
    """Test energy-related API endpoints"""
    
    def test_get_energy_consumption(self):
        """Test energy consumption endpoint"""
        response = client.get("/api/v1/energy/consumption")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_energy_consumption_with_filters(self):
        """Test energy consumption with filters"""
        params = {
            "meter_id": "SM001",
            "limit": 50
        }
        response = client.get("/api/v1/energy/consumption", params=params)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 50
    
    def test_get_consumption_summary(self):
        """Test consumption summary endpoint"""
        response = client.get("/api/v1/energy/consumption/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_consumption" in data
        assert "average_power" in data
        assert "peak_power" in data
    
    def test_get_hourly_consumption(self):
        """Test hourly consumption endpoint"""
        response = client.get("/api/v1/energy/consumption/hourly")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_smart_meters(self):
        """Test smart meters endpoint"""
        response = client.get("/api/v1/energy/meters")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestPricingAPI:
    """Test pricing-related API endpoints"""
    
    def test_get_current_price(self):
        """Test current price endpoint"""
        response = client.get("/api/v1/pricing/current")
        assert response.status_code == 200
        data = response.json()
        assert "price_per_kwh" in data
        assert "pricing_tier" in data
    
    def test_get_price_forecast(self):
        """Test price forecast endpoint"""
        response = client.get("/api/v1/pricing/forecast")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_pricing_tiers(self):
        """Test pricing tiers endpoint"""
        response = client.get("/api/v1/pricing/tiers")
        assert response.status_code == 200
        data = response.json()
        assert "current_tier" in data
        assert "tiers" in data
    
    def test_trigger_pricing_optimization(self):
        """Test pricing optimization trigger"""
        response = client.post("/api/v1/pricing/optimize")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data


class TestRenewableAPI:
    """Test renewable energy API endpoints"""
    
    def test_get_solar_generation(self):
        """Test solar generation endpoint"""
        response = client.get("/api/v1/renewable/solar/generation")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_wind_generation(self):
        """Test wind generation endpoint"""
        response = client.get("/api/v1/renewable/wind/generation")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_renewable_forecasts(self):
        """Test renewable forecasts endpoint"""
        response = client.get("/api/v1/renewable/forecasts?source_type=solar")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_renewable_summary(self):
        """Test renewable summary endpoint"""
        response = client.get("/api/v1/renewable/summary")
        assert response.status_code == 200
        data = response.json()
        assert "solar" in data
        assert "wind" in data


class TestMeterAPI:
    """Test smart meter management API endpoints"""
    
    def test_get_meters(self):
        """Test get meters endpoint"""
        response = client.get("/api/v1/meters/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_register_meter(self):
        """Test meter registration"""
        meter_data = {
            "meter_id": "TEST001",
            "location": "Test Location",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "meter_type": "residential",
            "installation_date": "2024-04-01T10:00:00Z",
            "firmware_version": "v2.1.3"
        }
        response = client.post("/api/v1/meters/register", json=meter_data)
        # May fail if meter already exists, which is expected
        assert response.status_code in [200, 201, 400]
    
    def test_submit_meter_reading(self):
        """Test meter reading submission"""
        reading_data = {
            "meter_id": "SM001",
            "timestamp": datetime.utcnow().isoformat(),
            "active_energy": 125.5,
            "active_power": 8.5,
            "voltage_l1": 230.2,
            "current_l1": 37.1,
            "power_factor": 0.95,
            "frequency": 50.0,
            "quality_flag": "good"
        }
        response = client.post("/api/v1/meters/data", json=reading_data)
        assert response.status_code in [200, 201, 404]  # 404 if meter doesn't exist


class TestPredictionAPI:
    """Test prediction API endpoints"""
    
    def test_get_energy_predictions(self):
        """Test energy predictions endpoint"""
        response = client.get("/api/v1/predictions/energy")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_model_status(self):
        """Test model status endpoint"""
        response = client.get("/api/v1/predictions/models/status")
        assert response.status_code == 200
        data = response.json()
        assert "lstm_model" in data
        assert "status" in data
    
    def test_get_prediction_accuracy(self):
        """Test prediction accuracy endpoint"""
        response = client.get("/api/v1/predictions/energy/accuracy")
        assert response.status_code == 200
        data = response.json()
        assert "predictions_analyzed" in data


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # May be unhealthy in test environment
        data = response.json()
        assert "status" in data


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_meter_id(self):
        """Test invalid meter ID handling"""
        response = client.get("/api/v1/energy/consumption?meter_id=INVALID")
        assert response.status_code == 200  # Should return empty list
        data = response.json()
        assert isinstance(data, list)
    
    def test_invalid_date_range(self):
        """Test invalid date range handling"""
        params = {
            "start_date": "invalid-date",
            "end_date": "2024-04-01T10:00:00Z"
        }
        response = client.get("/api/v1/energy/consumption", params=params)
        assert response.status_code == 422  # Validation error
    
    def test_large_limit(self):
        """Test large limit handling"""
        response = client.get("/api/v1/energy/consumption?limit=10000")
        assert response.status_code == 422  # Should reject large limits
    
    def test_negative_hours_ahead(self):
        """Test negative hours ahead parameter"""
        response = client.get("/api/v1/pricing/forecast?hours_ahead=-1")
        assert response.status_code == 422  # Validation error


class TestDataValidation:
    """Test data validation and schema compliance"""
    
    def test_meter_registration_validation(self):
        """Test meter registration data validation"""
        # Missing required fields
        invalid_data = {
            "meter_id": "TEST002"
            # Missing other required fields
        }
        response = client.post("/api/v1/meters/register", json=invalid_data)
        assert response.status_code == 422
    
    def test_reading_data_validation(self):
        """Test reading data validation"""
        # Invalid data types
        invalid_data = {
            "meter_id": "SM001",
            "timestamp": "invalid-timestamp",
            "active_energy": "not-a-number"
        }
        response = client.post("/api/v1/meters/data", json=invalid_data)
        assert response.status_code == 422


@pytest.mark.asyncio
class TestAsyncEndpoints:
    """Test asynchronous endpoint behavior"""
    
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            tasks = []
            for _ in range(10):
                task = ac.get("/api/v1/energy/consumption")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            for response in responses:
                assert response.status_code == 200


class TestPerformance:
    """Test API performance characteristics"""
    
    def test_response_time(self):
        """Test API response time"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/energy/consumption")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 2.0  # Should respond within 2 seconds
        assert response.status_code == 200
    
    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        response = client.get("/api/v1/energy/consumption?limit=1000")
        assert response.status_code in [200, 422]  # Either success or validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
