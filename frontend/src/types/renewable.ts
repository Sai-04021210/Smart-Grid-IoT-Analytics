/**
 * Renewable Energy TypeScript interfaces
 */

export interface SolarGeneration {
  id: number
  source_id: string
  timestamp: string
  power_output_kw: number
  energy_generated_kwh: number
  irradiance_wm2?: number
  temperature_c?: number
  capacity_factor?: number
  efficiency?: number
}

export interface WindGeneration {
  id: number
  source_id: string
  timestamp: string
  power_output_kw: number
  energy_generated_kwh: number
  wind_speed_ms?: number
  wind_direction_deg?: number
  temperature_c?: number
  capacity_factor?: number
  efficiency?: number
}

export interface RenewableSummary {
  solar: {
    total_power_kw: number
    total_energy_kwh: number
    avg_capacity_factor: number
    active_panels: number
  }
  wind: {
    total_power_kw: number
    total_energy_kwh: number
    avg_capacity_factor: number
    active_turbines: number
  }
  total_renewable_power: number
  total_renewable_energy: number
  renewable_percentage: number
}

export interface RenewableForecast {
  id: number
  source_id: string
  source_type: 'solar' | 'wind'
  forecast_timestamp: string
  target_timestamp: string
  predicted_power_kw: number
  predicted_energy_kwh: number
  confidence_interval_lower?: number
  confidence_interval_upper?: number
  model_version: string
}

