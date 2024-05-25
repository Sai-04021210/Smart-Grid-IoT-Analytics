/**
 * Energy Service - API calls for energy consumption data
 */

import { api } from './api'
import { EnergyReading, ConsumptionSummary, HourlyConsumption } from '../types/energy'

export const energyService = {
  /**
   * Get energy consumption readings
   */
  getConsumption: async (params?: {
    meter_id?: string
    start_date?: string
    end_date?: string
    limit?: number
  }): Promise<EnergyReading[]> => {
    return api.get('/api/v1/energy/consumption', { params })
  },

  /**
   * Get consumption summary statistics
   */
  getConsumptionSummary: async (params?: {
    meter_id?: string
    start_date?: string
    end_date?: string
  }): Promise<ConsumptionSummary> => {
    return api.get('/api/v1/energy/consumption/summary', { params })
  },

  /**
   * Get hourly consumption aggregated data
   */
  getHourlyConsumption: async (params?: {
    meter_id?: string
    hours?: number
  }): Promise<HourlyConsumption[]> => {
    return api.get('/api/v1/energy/consumption/hourly', { params })
  },

  /**
   * Get daily consumption aggregated data
   */
  getDailyConsumption: async (params?: {
    meter_id?: string
    days?: number
  }): Promise<any[]> => {
    return api.get('/api/v1/energy/consumption/daily', { params })
  },

  /**
   * Submit new energy reading
   */
  submitReading: async (reading: Partial<EnergyReading>): Promise<EnergyReading> => {
    return api.post('/api/v1/meters/data', reading)
  },
}

