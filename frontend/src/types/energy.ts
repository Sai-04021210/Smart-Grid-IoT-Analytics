/**
 * Energy-related TypeScript interfaces
 */

export interface EnergyReading {
  id: number
  meter_id: string
  timestamp: string
  active_energy: number
  reactive_energy?: number
  apparent_energy?: number
  active_power?: number
  reactive_power?: number
  power_factor?: number
  voltage_l1?: number
  voltage_l2?: number
  voltage_l3?: number
  current_l1?: number
  current_l2?: number
  current_l3?: number
  frequency?: number
  quality_flag: string
}

export interface ConsumptionSummary {
  total_consumption: number
  average_power: number
  peak_power: number
  reading_count: number
  start_date: string
  end_date: string
  meter_count: number
}

export interface HourlyConsumption {
  hour: string
  meter_id: string
  total_consumption: number
  avg_power: number
  peak_power: number
  reading_count: number
}

export interface EnergyStats {
  total_consumption: number
  avg_consumption: number
  peak_consumption: number
  min_consumption: number
  consumption_trend: number
}

