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
    // Backend uses panel_id instead of source_id, and limit instead of hours
    const apiParams: any = {}
    if (params?.source_id) {
      apiParams.panel_id = params.source_id
    }
    if (params?.hours) {
      // Approximate: assume 1 reading per minute, so hours * 60
      apiParams.limit = Math.min(params.hours * 60, 1000)
    } else {
      apiParams.limit = 100
    }
    return api.get('/api/v1/renewable/solar/generation', { params: apiParams })
  },

  /**
   * Get wind generation data
   */
  getWindGeneration: async (params?: {
    source_id?: string
    hours?: number
  }): Promise<WindGeneration[]> => {
    // Backend uses turbine_id instead of source_id, and limit instead of hours
    const apiParams: any = {}
    if (params?.source_id) {
      apiParams.turbine_id = params.source_id
    }
    if (params?.hours) {
      // Approximate: assume 1 reading per minute, so hours * 60
      apiParams.limit = Math.min(params.hours * 60, 1000)
    } else {
      apiParams.limit = 100
    }
    return api.get('/api/v1/renewable/wind/generation', { params: apiParams })
  },

  /**
   * Get renewable energy summary
   */
  getRenewableSummary: async (params?: {
    hours?: number
  }): Promise<RenewableSummary> => {
    // Backend uses 'period' parameter: hour, day, week, month
    // Map hours to period
    let period = 'day' // default
    if (params?.hours) {
      if (params.hours <= 24) period = 'hour'
      else if (params.hours <= 168) period = 'day' // 7 days
      else if (params.hours <= 720) period = 'week' // 30 days
      else period = 'month'
    }
    return api.get('/api/v1/renewable/summary', { params: { period } })
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

