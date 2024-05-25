/**
 * Custom hooks for pricing data
 */

import { useQuery, useMutation, useQueryClient } from 'react-query'
import { pricingService } from '../services/pricingService'
import toast from 'react-hot-toast'

/**
 * Hook to fetch current price
 */
export const useCurrentPrice = (meterType: string = 'residential') => {
  return useQuery(
    ['current-price', meterType],
    () => pricingService.getCurrentPrice(meterType),
    {
      staleTime: 60000, // 1 minute
      refetchInterval: 120000, // Refetch every 2 minutes
      onError: (error) => {
        console.error('Error fetching current price:', error)
      },
    }
  )
}

/**
 * Hook to fetch price forecast
 */
export const usePriceForecast = (params?: {
  hours_ahead?: number
  meter_type?: string
}) => {
  return useQuery(
    ['price-forecast', params],
    () => pricingService.getPriceForecast(params),
    {
      staleTime: 300000, // 5 minutes
      onError: (error) => {
        console.error('Error fetching price forecast:', error)
      },
    }
  )
}

/**
 * Hook to fetch pricing tiers
 */
export const usePricingTiers = () => {
  return useQuery(
    'pricing-tiers',
    () => pricingService.getPricingTiers(),
    {
      staleTime: 600000, // 10 minutes
      onError: (error) => {
        console.error('Error fetching pricing tiers:', error)
      },
    }
  )
}

/**
 * Hook to fetch dynamic pricing history
 */
export const useDynamicPricing = (params?: { hours?: number }) => {
  return useQuery(
    ['dynamic-pricing', params],
    () => pricingService.getDynamicPricing(params),
    {
      staleTime: 300000, // 5 minutes
      onError: (error) => {
        console.error('Error fetching dynamic pricing:', error)
      },
    }
  )
}

/**
 * Hook to trigger pricing optimization
 */
export const useOptimizePricing = () => {
  const queryClient = useQueryClient()

  return useMutation(
    () => pricingService.optimizePricing(),
    {
      onSuccess: () => {
        toast.success('Pricing optimization triggered')
        queryClient.invalidateQueries('current-price')
        queryClient.invalidateQueries('price-forecast')
        queryClient.invalidateQueries('dynamic-pricing')
      },
      onError: (error) => {
        console.error('Error optimizing pricing:', error)
        toast.error('Failed to trigger pricing optimization')
      },
    }
  )
}

