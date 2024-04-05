# Smart Grid IoT Analytics API Reference

## Overview

The Smart Grid IoT Analytics API provides comprehensive endpoints for managing energy data, predictions, renewable energy sources, and dynamic pricing. The API is built with FastAPI and follows RESTful principles.

**Base URL:** `http://localhost:8000/api/v1`

## Authentication

Currently, the API operates without authentication for development purposes. In production, implement JWT-based authentication.

## Energy Endpoints

### Get Energy Consumption Data

```http
GET /api/v1/energy/consumption
```

**Query Parameters:**
- `meter_id` (optional): Filter by specific meter ID
- `start_date` (optional): Start date for data range (ISO format)
- `end_date` (optional): End date for data range (ISO format)
- `limit` (optional): Maximum number of records (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 1,
    "meter_id": "SM001",
    "timestamp": "2024-04-01T10:00:00Z",
    "active_energy": 125.5,
    "reactive_energy": 15.2,
    "active_power": 8.5,
    "voltage_l1": 230.2,
    "current_l1": 37.1,
    "power_factor": 0.95,
    "frequency": 50.0,
    "quality_flag": "good",
    "created_at": "2024-04-01T10:00:05Z"
  }
]
```

### Get Consumption Summary

```http
GET /api/v1/energy/consumption/summary
```

**Query Parameters:**
- `meter_id` (optional): Filter by specific meter ID
- `period`: Aggregation period (`hour`, `day`, `week`, `month`)

**Response:**
```json
{
  "total_consumption": 2450.5,
  "average_power": 12.3,
  "peak_power": 25.8,
  "reading_count": 168,
  "period": "week",
  "start_time": "2024-03-25T00:00:00Z",
  "end_time": "2024-04-01T00:00:00Z"
}
```

### Get Hourly Consumption

```http
GET /api/v1/energy/consumption/hourly
```

**Query Parameters:**
- `meter_id` (optional): Filter by specific meter ID
- `days` (optional): Number of days to include (default: 7, max: 30)

**Response:**
```json
[
  {
    "timestamp": "2024-04-01T10:00:00Z",
    "total_consumption": 125.5,
    "average_power": 8.5,
    "reading_count": 4
  }
]
```

### Get Smart Meters

```http
GET /api/v1/energy/meters
```

**Query Parameters:**
- `is_active` (optional): Filter by active status
- `meter_type` (optional): Filter by meter type

**Response:**
```json
[
  {
    "meter_id": "SM001",
    "location": "Residential Area A - House 1",
    "meter_type": "residential",
    "is_active": true,
    "last_communication": "2024-04-01T10:00:00Z",
    "installation_date": "2023-01-15T10:00:00Z"
  }
]
```

## Pricing Endpoints

### Get Current Energy Price

```http
GET /api/v1/pricing/current
```

**Query Parameters:**
- `meter_type` (optional): Type of meter (`residential`, `commercial`, `industrial`)

**Response:**
```json
{
  "price_per_kwh": 0.145,
  "meter_type": "residential",
  "timestamp": "2024-04-01T10:00:00Z",
  "pricing_tier": "peak"
}
```

### Get Price Forecast

```http
GET /api/v1/pricing/forecast
```

**Query Parameters:**
- `hours_ahead` (optional): Number of hours to forecast (default: 24)

**Response:**
```json
[
  {
    "timestamp": "2024-04-01T11:00:00Z",
    "price_per_kwh": 0.142,
    "adjustment_factor": 1.18,
    "predicted_demand": 1250.5,
    "renewable_generation": 320.8
  }
]
```

## Renewable Energy Endpoints

### Get Solar Generation Data

```http
GET /api/v1/renewable/solar/generation
```

**Query Parameters:**
- `panel_id` (optional): Filter by specific panel ID
- `start_date` (optional): Start date for data range
- `end_date` (optional): End date for data range
- `limit` (optional): Maximum number of records

**Response:**
```json
[
  {
    "id": 1,
    "source_id": "SP001",
    "timestamp": "2024-04-01T12:00:00Z",
    "power_output_kw": 8.5,
    "energy_generated_kwh": 8.5,
    "irradiance_wm2": 850.2,
    "temperature_c": 25.3,
    "capacity_factor": 0.81,
    "efficiency": 0.20
  }
]
```

### Get Wind Generation Data

```http
GET /api/v1/renewable/wind/generation
```

**Query Parameters:**
- `turbine_id` (optional): Filter by specific turbine ID
- `start_date` (optional): Start date for data range
- `end_date` (optional): End date for data range
- `limit` (optional): Maximum number of records

**Response:**
```json
[
  {
    "id": 1,
    "source_id": "WT001",
    "timestamp": "2024-04-01T12:00:00Z",
    "power_output_kw": 1850.0,
    "energy_generated_kwh": 1850.0,
    "wind_speed_ms": 12.5,
    "wind_direction_deg": 225.0,
    "temperature_c": 18.2,
    "capacity_factor": 0.925
  }
]
```

### Get Renewable Forecasts

```http
GET /api/v1/renewable/forecasts
```

**Query Parameters:**
- `source_type`: Type of renewable source (`solar`, `wind`)
- `hours_ahead` (optional): Number of hours to forecast (default: 24)

**Response:**
```json
[
  {
    "source_id": "SP001",
    "source_type": "solar",
    "timestamp": "2024-04-01T13:00:00Z",
    "predicted_power_kw": 9.2,
    "predicted_energy_kwh": 9.2,
    "confidence_lower": 8.1,
    "confidence_upper": 10.3,
    "predicted_irradiance_wm2": 920.0,
    "predicted_temperature_c": 26.1
  }
]
```

## Prediction Endpoints

### Get Energy Predictions

```http
GET /api/v1/predictions/energy
```

**Query Parameters:**
- `meter_id` (optional): Filter by specific meter ID
- `hours_ahead` (optional): Number of hours to predict (default: 24)

**Response:**
```json
[
  {
    "meter_id": "SM001",
    "prediction_timestamp": "2024-04-01T10:00:00Z",
    "target_timestamp": "2024-04-01T11:00:00Z",
    "predicted_consumption": 125.8,
    "confidence_interval_lower": 118.2,
    "confidence_interval_upper": 133.4,
    "model_version": "lstm_v1.0",
    "model_type": "lstm"
  }
]
```

## Smart Meter Management

### Submit Meter Reading

```http
POST /api/v1/meters/data
```

**Request Body:**
```json
{
  "meter_id": "SM001",
  "timestamp": "2024-04-01T10:00:00Z",
  "active_energy": 125.5,
  "reactive_energy": 15.2,
  "active_power": 8.5,
  "voltage_l1": 230.2,
  "current_l1": 37.1,
  "power_factor": 0.95,
  "frequency": 50.0,
  "quality_flag": "good"
}
```

**Response:**
```json
{
  "id": 1,
  "meter_id": "SM001",
  "timestamp": "2024-04-01T10:00:00Z",
  "status": "created"
}
```

### Register Smart Meter

```http
POST /api/v1/meters/register
```

**Request Body:**
```json
{
  "meter_id": "SM006",
  "location": "New Installation Site",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "meter_type": "residential",
  "installation_date": "2024-04-01T10:00:00Z",
  "firmware_version": "v2.1.3"
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

**Error Response Format:**
```json
{
  "detail": "Error message description",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-04-01T10:00:00Z"
}
```

## Rate Limiting

API requests are limited to:
- 1000 requests per hour for read operations
- 100 requests per hour for write operations

## WebSocket Endpoints

### Real-time Energy Data

```
ws://localhost:8000/ws/energy/{meter_id}
```

Provides real-time energy consumption updates for a specific meter.

### Grid Status Updates

```
ws://localhost:8000/ws/grid/status
```

Provides real-time grid status and alert notifications.

## MQTT Integration

The API integrates with MQTT for real-time data collection:

**Topics:**
- `smartgrid/meters/{meter_id}/data` - Smart meter readings
- `smartgrid/solar/{panel_id}/data` - Solar panel data
- `smartgrid/wind/{turbine_id}/data` - Wind turbine data
- `smartgrid/grid/status` - Grid status updates
- `smartgrid/pricing/update` - Pricing updates
