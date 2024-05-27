/**
 * Custom hooks for smart meter data
 */

import { useQuery, useMutation, useQueryClient } from 'react-query'
import { meterService } from '../services/meterService'
import { MeterRegistration } from '../types/meter'
import toast from 'react-hot-toast'

/**
 * Hook to fetch all meters
 */
export const useMeters = (params?: {
  meter_type?: string
  is_active?: boolean
}) => {
  return useQuery(
    ['meters', params],
    () => meterService.getMeters(params),
    {
      staleTime: 120000, // 2 minutes
      onError: (error) => {
        console.error('Error fetching meters:', error)
      },
    }
  )
}

/**
 * Hook to fetch a specific meter
 */
export const useMeter = (meterId: string) => {
  return useQuery(
    ['meter', meterId],
    () => meterService.getMeter(meterId),
    {
      enabled: !!meterId,
      staleTime: 120000, // 2 minutes
      onError: (error) => {
        console.error('Error fetching meter:', error)
      },
    }
  )
}

/**
 * Hook to register a new meter
 */
export const useRegisterMeter = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (meter: MeterRegistration) => meterService.registerMeter(meter),
    {
      onSuccess: () => {
        toast.success('Meter registered successfully')
        queryClient.invalidateQueries('meters')
      },
      onError: (error: any) => {
        console.error('Error registering meter:', error)
        const message = error.response?.data?.detail || 'Failed to register meter'
        toast.error(message)
      },
    }
  )
}

/**
 * Hook to update meter
 */
export const useUpdateMeter = () => {
  const queryClient = useQueryClient()

  return useMutation(
    ({ meterId, updates }: { meterId: string; updates: any }) =>
      meterService.updateMeter(meterId, updates),
    {
      onSuccess: (_, variables) => {
        toast.success('Meter updated successfully')
        queryClient.invalidateQueries(['meter', variables.meterId])
        queryClient.invalidateQueries('meters')
      },
      onError: (error) => {
        console.error('Error updating meter:', error)
        toast.error('Failed to update meter')
      },
    }
  )
}

/**
 * Hook to deactivate meter
 */
export const useDeactivateMeter = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (meterId: string) => meterService.deactivateMeter(meterId),
    {
      onSuccess: () => {
        toast.success('Meter deactivated successfully')
        queryClient.invalidateQueries('meters')
      },
      onError: (error) => {
        console.error('Error deactivating meter:', error)
        toast.error('Failed to deactivate meter')
      },
    }
  )
}

/**
 * Hook to fetch meter statistics
 * Note: This endpoint doesn't exist yet in the backend, so we disable it
 */
export const useMeterStats = () => {
  return useQuery(
    'meter-stats',
    () => meterService.getMeterStats(),
    {
      enabled: false, // Disable until backend endpoint is implemented
      staleTime: 120000, // 2 minutes
      onError: (error) => {
        console.error('Error fetching meter stats:', error)
      },
    }
  )
}

