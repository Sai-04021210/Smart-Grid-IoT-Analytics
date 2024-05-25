/**
 * Prediction Service - API calls for ML predictions
 */

import { api } from './api'
import {
  EnergyPrediction,
  ModelStatus,
  PredictionAccuracy,
  PredictionGenerateResponse,
} from '../types/prediction'

export const predictionService = {
  /**
   * Get energy consumption predictions
   */
  getEnergyPredictions: async (params?: {
    meter_id?: string
    hours_ahead?: number
  }): Promise<EnergyPrediction[]> => {
    return api.get('/api/v1/predictions/energy', { params })
  },

  /**
   * Generate new predictions
   */
  generatePredictions: async (meterId?: string): Promise<PredictionGenerateResponse> => {
    const params = meterId ? { meter_id: meterId } : undefined
    return api.post('/api/v1/predictions/energy/generate', null, { params })
  },

  /**
   * Get prediction accuracy metrics
   */
  getPredictionAccuracy: async (params?: {
    meter_id?: string
    days?: number
  }): Promise<PredictionAccuracy> => {
    return api.get('/api/v1/predictions/energy/accuracy', { params })
  },

  /**
   * Get ML model status
   */
  getModelStatus: async (): Promise<ModelStatus> => {
    return api.get('/api/v1/predictions/models/status')
  },

  /**
   * Trigger model retraining
   */
  retrainModel: async (meterId?: string): Promise<any> => {
    const params = meterId ? { meter_id: meterId } : undefined
    return api.post('/api/v1/predictions/models/retrain', null, { params })
  },
}

