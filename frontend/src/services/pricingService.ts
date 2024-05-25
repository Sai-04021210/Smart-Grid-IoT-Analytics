/**
 * Pricing Service - API calls for energy pricing
 */

import { api } from './api'
import { CurrentPrice, PriceForecast, PricingTiers, DynamicPricing } from '../types/pricing'

export const pricingService = {
  /**
   * Get current energy price
   */
  getCurrentPrice: async (meterType: string = 'residential'): Promise<CurrentPrice> => {
    return api.get('/api/v1/pricing/current', {
      params: { meter_type: meterType },
    })
  },

  /**
   * Get price forecast
   */
  getPriceForecast: async (params?: {
    hours_ahead?: number
    meter_type?: string
  }): Promise<PriceForecast[]> => {
    return api.get('/api/v1/pricing/forecast', { params })
  },

  /**
   * Get pricing tiers information
   */
  getPricingTiers: async (): Promise<PricingTiers> => {
    return api.get('/api/v1/pricing/tiers')
  },

  /**
   * Get dynamic pricing history
   */
  getDynamicPricing: async (params?: {
    hours?: number
  }): Promise<DynamicPricing[]> => {
    return api.get('/api/v1/pricing/dynamic', { params })
  },

  /**
   * Trigger pricing optimization
   */
  optimizePricing: async (): Promise<any> => {
    return api.post('/api/v1/pricing/optimize')
  },
}

