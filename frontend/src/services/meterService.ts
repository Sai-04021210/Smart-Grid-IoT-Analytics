/**
 * Meter Service - API calls for smart meter management
 */

import { api } from './api'
import { SmartMeter, MeterRegistration, MeterStats } from '../types/meter'

export const meterService = {
  /**
   * Get all smart meters
   */
  getMeters: async (params?: {
    meter_type?: string
    is_active?: boolean
  }): Promise<SmartMeter[]> => {
    return api.get('/api/v1/meters/', { params })
  },

  /**
   * Get a specific meter by ID
   */
  getMeter: async (meterId: string): Promise<SmartMeter> => {
    return api.get(`/api/v1/meters/${meterId}`)
  },

  /**
   * Register a new smart meter
   */
  registerMeter: async (meter: MeterRegistration): Promise<SmartMeter> => {
    return api.post('/api/v1/meters/register', meter)
  },

  /**
   * Update meter information
   */
  updateMeter: async (meterId: string, updates: Partial<SmartMeter>): Promise<SmartMeter> => {
    return api.put(`/api/v1/meters/${meterId}`, updates)
  },

  /**
   * Deactivate a meter
   */
  deactivateMeter: async (meterId: string): Promise<void> => {
    return api.post(`/api/v1/meters/${meterId}/deactivate`)
  },

  /**
   * Get meter statistics
   */
  getMeterStats: async (): Promise<MeterStats> => {
    return api.get('/api/v1/meters/stats')
  },
}

