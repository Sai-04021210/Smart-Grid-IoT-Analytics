/**
 * Renewable Energy Service - API calls for solar and wind generation
 */

import { api } from './api'
import {
  SolarGeneration,
  WindGeneration,
  RenewableSummary,
  RenewableForecast,
} from '../types/renewable'

export const renewableService = {
  /**
   * Get solar generation data
   */
  getSolarGeneration: async (params?: {
    source_id?: string
    hours?: number
  }): Promise<SolarGeneration[]> => {
    return api.get('/api/v1/renewable/solar/generation', { params })
  },

  /**
   * Get wind generation data
   */
  getWindGeneration: async (params?: {
    source_id?: string
    hours?: number
  }): Promise<WindGeneration[]> => {
    return api.get('/api/v1/renewable/wind/generation', { params })
  },

  /**
   * Get renewable energy summary
   */
  getRenewableSummary: async (params?: {
    hours?: number
  }): Promise<RenewableSummary> => {
    return api.get('/api/v1/renewable/summary', { params })
  },

  /**
   * Get renewable energy forecasts
   */
  getRenewableForecasts: async (params: {
    source_type: 'solar' | 'wind'
    hours_ahead?: number
  }): Promise<RenewableForecast[]> => {
    return api.get('/api/v1/renewable/forecasts', { params })
  },

  /**
   * Get all renewable sources (panels and turbines)
   */
  getRenewableSources: async (): Promise<any> => {
    return api.get('/api/v1/renewable/sources')
  },
}

