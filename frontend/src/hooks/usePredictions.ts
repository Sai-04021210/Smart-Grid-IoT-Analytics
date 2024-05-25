/**
 * Custom hooks for ML predictions
 */

import { useQuery, useMutation, useQueryClient } from 'react-query'
import { predictionService } from '../services/predictionService'
import toast from 'react-hot-toast'

/**
 * Hook to fetch energy predictions
 */
export const useEnergyPredictions = (params?: {
  meter_id?: string
  hours_ahead?: number
}) => {
  return useQuery(
    ['energy-predictions', params],
    () => predictionService.getEnergyPredictions(params),
    {
      staleTime: 300000, // 5 minutes
      onError: (error) => {
        console.error('Error fetching predictions:', error)
      },
    }
  )
}

/**
 * Hook to generate new predictions
 */
export const useGeneratePredictions = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (meterId?: string) => predictionService.generatePredictions(meterId),
    {
      onSuccess: (data) => {
        toast.success(data.message || 'Predictions generated successfully')
        queryClient.invalidateQueries('energy-predictions')
      },
      onError: (error) => {
        console.error('Error generating predictions:', error)
        toast.error('Failed to generate predictions')
      },
    }
  )
}

/**
 * Hook to fetch prediction accuracy
 */
export const usePredictionAccuracy = (params?: {
  meter_id?: string
  days?: number
}) => {
  return useQuery(
    ['prediction-accuracy', params],
    () => predictionService.getPredictionAccuracy(params),
    {
      staleTime: 600000, // 10 minutes
      onError: (error) => {
        console.error('Error fetching prediction accuracy:', error)
      },
    }
  )
}

/**
 * Hook to fetch model status
 */
export const useModelStatus = () => {
  return useQuery(
    'model-status',
    () => predictionService.getModelStatus(),
    {
      staleTime: 300000, // 5 minutes
      refetchInterval: 600000, // Refetch every 10 minutes
      onError: (error) => {
        console.error('Error fetching model status:', error)
      },
    }
  )
}

/**
 * Hook to retrain model
 */
export const useRetrainModel = () => {
  const queryClient = useQueryClient()

  return useMutation(
    (meterId?: string) => predictionService.retrainModel(meterId),
    {
      onSuccess: () => {
        toast.success('Model retraining started')
        queryClient.invalidateQueries('model-status')
      },
      onError: (error) => {
        console.error('Error retraining model:', error)
        toast.error('Failed to start model retraining')
      },
    }
  )
}

