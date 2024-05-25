/**
 * Custom hooks for renewable energy data
 */

import { useQuery } from 'react-query'
import { renewableService } from '../services/renewableService'

/**
 * Hook to fetch solar generation data
 */
export const useSolarGeneration = (params?: {
  source_id?: string
  hours?: number
}) => {
  return useQuery(
    ['solar-generation', params],
    () => renewableService.getSolarGeneration(params),
    {
      staleTime: 60000, // 1 minute
      refetchInterval: 120000, // Refetch every 2 minutes
      onError: (error) => {
        console.error('Error fetching solar generation:', error)
      },
    }
  )
}

/**
 * Hook to fetch wind generation data
 */
export const useWindGeneration = (params?: {
  source_id?: string
  hours?: number
}) => {
  return useQuery(
    ['wind-generation', params],
    () => renewableService.getWindGeneration(params),
    {
      staleTime: 60000, // 1 minute
      refetchInterval: 120000, // Refetch every 2 minutes
      onError: (error) => {
        console.error('Error fetching wind generation:', error)
      },
    }
  )
}

/**
 * Hook to fetch renewable energy summary
 */
export const useRenewableSummary = (params?: { hours?: number }) => {
  return useQuery(
    ['renewable-summary', params],
    () => renewableService.getRenewableSummary(params),
    {
      staleTime: 60000, // 1 minute
      refetchInterval: 120000, // Refetch every 2 minutes
      onError: (error) => {
        console.error('Error fetching renewable summary:', error)
      },
    }
  )
}

/**
 * Hook to fetch renewable forecasts
 */
export const useRenewableForecasts = (params: {
  source_type: 'solar' | 'wind'
  hours_ahead?: number
}) => {
  return useQuery(
    ['renewable-forecasts', params],
    () => renewableService.getRenewableForecasts(params),
    {
      enabled: !!params.source_type,
      staleTime: 300000, // 5 minutes
      onError: (error) => {
        console.error('Error fetching renewable forecasts:', error)
      },
    }
  )
}

/**
 * Hook to fetch all renewable sources
 */
export const useRenewableSources = () => {
  return useQuery(
    'renewable-sources',
    () => renewableService.getRenewableSources(),
    {
      staleTime: 300000, // 5 minutes
      onError: (error) => {
        console.error('Error fetching renewable sources:', error)
      },
    }
  )
}

