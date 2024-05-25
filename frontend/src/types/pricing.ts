/**
 * Pricing-related TypeScript interfaces
 */

export interface CurrentPrice {
  price_per_kwh: number
  pricing_tier: string
  timestamp: string
  peak_price?: number
  off_peak_price?: number
  base_price?: number
  time_of_use_period?: string
}

export interface PriceForecast {
  timestamp: string
  predicted_price: number
  pricing_tier: string
  demand_level: string
  renewable_percentage?: number
}

export interface PricingTiers {
  current_tier: string
  tiers: {
    name: string
    price_per_kwh: number
    description: string
    time_range?: string
  }[]
}

export interface DynamicPricing {
  id: number
  optimization_timestamp: string
  target_timestamp: string
  optimized_price_kwh: number
  price_adjustment_factor: number
  predicted_demand_kw: number
  predicted_supply_kw: number
  renewable_generation_kw?: number
  grid_congestion_level?: number
}

