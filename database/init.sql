-- Smart Grid IoT Analytics Database Initialization
-- PostgreSQL initialization script

-- Create database if not exists (handled by Docker)
-- CREATE DATABASE smartgrid;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb" CASCADE;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS smartgrid;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Set default schema
SET search_path TO smartgrid, public;

-- Create sample smart meters
INSERT INTO smart_meters (meter_id, location, latitude, longitude, meter_type, installation_date, is_active, firmware_version) VALUES
('SM001', 'Residential Area A - House 1', 40.7128, -74.0060, 'residential', '2023-01-15 10:00:00', true, 'v2.1.3'),
('SM002', 'Residential Area A - House 2', 40.7130, -74.0058, 'residential', '2023-01-16 11:00:00', true, 'v2.1.3'),
('SM003', 'Commercial District - Office Building', 40.7589, -73.9851, 'commercial', '2023-02-01 09:00:00', true, 'v2.2.1'),
('SM004', 'Industrial Zone - Factory 1', 40.6892, -74.0445, 'industrial', '2023-02-15 14:00:00', true, 'v2.2.1'),
('SM005', 'Residential Area B - Apartment Complex', 40.7505, -73.9934, 'residential', '2023-03-01 12:00:00', true, 'v2.1.3')
ON CONFLICT (meter_id) DO NOTHING;

-- Create sample solar panels
INSERT INTO solar_panels (panel_id, location, latitude, longitude, capacity_kw, panel_area_m2, efficiency, tilt_angle, azimuth_angle, installation_date, is_active) VALUES
('SP001', 'Residential Solar Farm A', 40.7128, -74.0060, 10.5, 65.0, 0.20, 30.0, 180.0, '2023-01-20 10:00:00', true),
('SP002', 'Commercial Building Rooftop', 40.7589, -73.9851, 25.0, 150.0, 0.22, 25.0, 180.0, '2023-02-10 11:00:00', true),
('SP003', 'Community Solar Garden', 40.7505, -73.9934, 50.0, 300.0, 0.21, 35.0, 180.0, '2023-03-05 09:00:00', true)
ON CONFLICT (panel_id) DO NOTHING;

-- Create sample wind turbines
INSERT INTO wind_turbines (turbine_id, location, latitude, longitude, capacity_kw, rotor_diameter_m, hub_height_m, cut_in_speed_ms, cut_out_speed_ms, rated_speed_ms, installation_date, is_active) VALUES
('WT001', 'Offshore Wind Farm - Turbine 1', 40.5000, -74.2000, 2000.0, 120.0, 90.0, 3.0, 25.0, 12.0, '2023-01-10 08:00:00', true),
('WT002', 'Offshore Wind Farm - Turbine 2', 40.5010, -74.2010, 2000.0, 120.0, 90.0, 3.0, 25.0, 12.0, '2023-01-12 08:00:00', true),
('WT003', 'Onshore Wind Farm - Turbine 1', 40.8000, -74.1000, 1500.0, 100.0, 80.0, 3.5, 25.0, 13.0, '2023-02-20 10:00:00', true)
ON CONFLICT (turbine_id) DO NOTHING;

-- Create sample energy prices
INSERT INTO energy_prices (timestamp, base_price_kwh, peak_price_kwh, off_peak_price_kwh, peak_start_hour, peak_end_hour, season, seasonal_multiplier, wholesale_price, transmission_cost, distribution_cost) VALUES
(NOW() - INTERVAL '1 hour', 0.12, 0.18, 0.096, 17, 21, 'spring', 1.0, 0.08, 0.02, 0.02),
(NOW(), 0.12, 0.18, 0.096, 17, 21, 'spring', 1.0, 0.08, 0.02, 0.02)
ON CONFLICT DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_energy_readings_meter_timestamp ON energy_readings(meter_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_energy_readings_timestamp ON energy_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_energy_predictions_meter_target ON energy_predictions(meter_id, target_timestamp);
CREATE INDEX IF NOT EXISTS idx_renewable_generation_source_timestamp ON renewable_energy_generation(source_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_renewable_forecasts_source_target ON renewable_forecasts(source_id, target_timestamp);
CREATE INDEX IF NOT EXISTS idx_dynamic_pricing_target ON dynamic_pricing(target_timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);

-- Create TimescaleDB hypertables for time-series data (if TimescaleDB is available)
-- SELECT create_hypertable('energy_readings', 'timestamp', if_not_exists => TRUE);
-- SELECT create_hypertable('renewable_energy_generation', 'timestamp', if_not_exists => TRUE);
-- SELECT create_hypertable('market_data', 'timestamp', if_not_exists => TRUE);

-- Create views for common queries
CREATE OR REPLACE VIEW v_latest_meter_readings AS
SELECT DISTINCT ON (meter_id) 
    meter_id,
    timestamp,
    active_energy,
    active_power,
    voltage_l1,
    current_l1,
    power_factor,
    quality_flag
FROM energy_readings
ORDER BY meter_id, timestamp DESC;

CREATE OR REPLACE VIEW v_hourly_consumption AS
SELECT 
    meter_id,
    date_trunc('hour', timestamp) as hour,
    SUM(active_energy) as total_consumption,
    AVG(active_power) as avg_power,
    MAX(active_power) as peak_power,
    COUNT(*) as reading_count
FROM energy_readings
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY meter_id, date_trunc('hour', timestamp)
ORDER BY meter_id, hour;

CREATE OR REPLACE VIEW v_renewable_summary AS
SELECT 
    source_type,
    date_trunc('hour', timestamp) as hour,
    SUM(power_output_kw) as total_power,
    SUM(energy_generated_kwh) as total_energy,
    AVG(capacity_factor) as avg_capacity_factor,
    COUNT(*) as reading_count
FROM renewable_energy_generation
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY source_type, date_trunc('hour', timestamp)
ORDER BY source_type, hour;

-- Create functions for data analysis
CREATE OR REPLACE FUNCTION get_meter_consumption_stats(meter_id_param TEXT, days_back INTEGER DEFAULT 7)
RETURNS TABLE(
    total_consumption NUMERIC,
    avg_power NUMERIC,
    peak_power NUMERIC,
    reading_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        SUM(er.active_energy)::NUMERIC as total_consumption,
        AVG(er.active_power)::NUMERIC as avg_power,
        MAX(er.active_power)::NUMERIC as peak_power,
        COUNT(*)::BIGINT as reading_count
    FROM energy_readings er
    WHERE er.meter_id = meter_id_param
    AND er.timestamp >= NOW() - (days_back || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for updating meter last_communication
CREATE OR REPLACE FUNCTION update_meter_last_communication()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE smart_meters 
    SET last_communication = NEW.timestamp
    WHERE meter_id = NEW.meter_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_meter_communication
    AFTER INSERT ON energy_readings
    FOR EACH ROW
    EXECUTE FUNCTION update_meter_last_communication();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smartgrid_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smartgrid_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO smartgrid_user;

-- Create monitoring tables
CREATE TABLE IF NOT EXISTS system_health (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    service_name VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_usage FLOAT,
    response_time_ms INTEGER,
    error_count INTEGER DEFAULT 0,
    details JSONB
);

-- Insert initial system health record
INSERT INTO system_health (service_name, status, details) VALUES
('database', 'healthy', '{"message": "Database initialized successfully"}');

COMMIT;
