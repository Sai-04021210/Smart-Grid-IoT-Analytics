/**
 * Custom hooks for energy data fetching
 */

import { useQuery, useMutation, useQueryClient } from 'react-query'
import { energyService } from '../services/energyService'
import toast from 'react-hot-toast'

/**
 * Hook to fetch energy consumption data
 */
export const useEnergyConsumption = (params?: {
  meter_id?: string
  start_date?: string
  end_date?: string
  limit?: number
}) => {
  return useQuery(
    ['energy-consumption', params],
    () => energyService.getConsumption(params),
    {
      staleTime: 30000, // 30 seconds
      refetchInterval: 60000, // Refetch every minute
      onError: (error) => {
        console.error('Error fetching energy consumption:', error)
      },
    }
  )
}

/**
 * Hook to fetch consumption summary
 */
export const useConsumptionSummary = (params?: {
  meter_id?: string
  start_date?: string
  end_date?: string
}) => {
  return useQuery(
    ['consumption-summary', params],
    () => energyService.getConsumptionSummary(params),
    {
      staleTime: 60000, // 1 minute
      refetchInterval: 120000, // Refetch every 2 minutes
      onError: (error) => {
        console.error('Error fetching consumption summary:', error)
      },
    }
  )
}

/**
 * Hook to fetch hourly consumption
 */
export const useHourlyConsumption = (params?: {
  meter_id?: string
  hours?: number
}) => {
  return useQuery(
    ['hourly-consumption', params],
    () => energyService.getHourlyConsumption(params),
    {
      staleTime: 60000, // 1 minute
      refetchInterval: 120000, // Refetch every 2 minutes
      onError: (error) => {
        console.error('Error fetching hourly consumption:', error)
      },
    }
  )
}

/**
 * Hook to fetch daily consumption
 */
export const useDailyConsumption = (params?: {
  meter_id?: string
  days?: number
}) => {
  return useQuery(
    ['daily-consumption', params],
    () => energyService.getDailyConsumption(params),
    {
      staleTime: 300000, // 5 minutes
      onError: (error) => {
        console.error('Error fetching daily consumption:', error)
      },
    }
  )
}

/**
 * Hook to submit energy reading
 */
export const useSubmitReading = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (reading: any) => energyService.submitReading(reading),
    {
      onSuccess: () => {
        toast.success('Energy reading submitted successfully')
        // Invalidate and refetch energy queries
        queryClient.invalidateQueries('energy-consumption')
        queryClient.invalidateQueries('consumption-summary')
        queryClient.invalidateQueries('hourly-consumption')
      },
      onError: (error) => {
        console.error('Error submitting reading:', error)
        toast.error('Failed to submit energy reading')
      },
    }
  )
}

