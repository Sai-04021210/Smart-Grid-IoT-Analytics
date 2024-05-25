/**
 * Smart Meter TypeScript interfaces
 */

export interface SmartMeter {
  id?: number
  meter_id: string
  location: string
  latitude?: number
  longitude?: number
  meter_type: 'residential' | 'commercial' | 'industrial'
  installation_date: string
  is_active: boolean
  firmware_version?: string
  last_communication?: string
  created_at?: string
  updated_at?: string
}

export interface MeterRegistration {
  meter_id: string
  location: string
  latitude?: number
  longitude?: number
  meter_type: 'residential' | 'commercial' | 'industrial'
  installation_date: string
  firmware_version?: string
}

export interface MeterStats {
  total_meters: number
  active_meters: number
  inactive_meters: number
  by_type: {
    residential: number
    commercial: number
    industrial: number
  }
}

