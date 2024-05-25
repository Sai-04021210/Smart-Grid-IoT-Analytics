/**
 * Prediction-related TypeScript interfaces
 */

export interface EnergyPrediction {
  id: number
  meter_id: string
  prediction_timestamp: string
  target_timestamp: string
  predicted_consumption: number
  confidence_interval_lower?: number
  confidence_interval_upper?: number
  prediction_accuracy?: number
  model_version: string
  model_type: string
  created_at: string
}

export interface ModelStatus {
  lstm_model: {
    loaded: boolean
    version: string
    sequence_length: number
    prediction_horizon: number
    model_path: string
  }
  status: string
  timestamp: string
}

export interface PredictionAccuracy {
  message?: string
  analysis_period_days: number
  predictions_analyzed: number
  average_accuracy?: number
  mae?: number
  rmse?: number
  mape?: number
  accuracy_by_meter?: Record<string, number>
}

export interface PredictionGenerateResponse {
  message: string
  meter_id?: string
  predictions_count?: number
  timestamp: string
}

