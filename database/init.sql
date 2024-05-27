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

-- Note: Tables will be created by SQLAlchemy models in the backend
-- Sample data will be inserted by the backend initialization or data generator

-- Create indexes for better performance (will be created after tables exist)
-- CREATE INDEX IF NOT EXISTS idx_energy_readings_meter_timestamp ON energy_readings(meter_id, timestamp);
-- CREATE INDEX IF NOT EXISTS idx_energy_readings_timestamp ON energy_readings(timestamp);
-- CREATE INDEX IF NOT EXISTS idx_energy_predictions_meter_target ON energy_predictions(meter_id, target_timestamp);
-- CREATE INDEX IF NOT EXISTS idx_renewable_generation_source_timestamp ON renewable_energy_generation(source_id, timestamp);
-- CREATE INDEX IF NOT EXISTS idx_renewable_forecasts_source_target ON renewable_forecasts(source_id, target_timestamp);
-- CREATE INDEX IF NOT EXISTS idx_dynamic_pricing_target ON dynamic_pricing(target_timestamp);
-- CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);

-- Create TimescaleDB hypertables for time-series data (if TimescaleDB is available)
-- SELECT create_hypertable('energy_readings', 'timestamp', if_not_exists => TRUE);
-- SELECT create_hypertable('renewable_energy_generation', 'timestamp', if_not_exists => TRUE);
-- SELECT create_hypertable('market_data', 'timestamp', if_not_exists => TRUE);

-- Note: Views, functions, triggers, and indexes will be created after tables are initialized by the backend

-- Grant permissions (user will be created by backend if needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smartgrid_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smartgrid_user;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO smartgrid_user;
