"""
LSTM Neural Network for Energy Consumption Prediction
Real-time energy demand forecasting using deep learning
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.smart_meter import EnergyReading, EnergyPrediction, SmartMeter
from app.services.weather_service import WeatherService

logger = logging.getLogger(__name__)


class LSTMPredictor:
    """LSTM-based energy consumption predictor"""
    
    def __init__(self):
        self.sequence_length = settings.LSTM_SEQUENCE_LENGTH  # 168 hours (7 days)
        self.prediction_horizon = settings.PREDICTION_HORIZON_HOURS  # 24 hours
        self.model = None
        self.scaler = None
        self.feature_scaler = None
        self.model_version = "lstm_v1.0"
        self.weather_service = WeatherService()
        
        # Model paths
        self.model_dir = "/app/ml-models/lstm"
        self.model_path = f"{self.model_dir}/lstm_energy_model.h5"
        self.scaler_path = f"{self.model_dir}/energy_scaler.pkl"
        self.feature_scaler_path = f"{self.model_dir}/feature_scaler.pkl"
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
    
    def prepare_data(self, meter_id: Optional[str] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training data from database"""
        try:
            db = SessionLocal()
            
            # Get historical energy readings
            query = db.query(EnergyReading).order_by(EnergyReading.timestamp.asc())
            
            if meter_id:
                query = query.filter(EnergyReading.meter_id == meter_id)
            
            # Get data from last 6 months for training
            start_date = datetime.utcnow() - timedelta(days=180)
            query = query.filter(EnergyReading.timestamp >= start_date)
            
            readings = query.all()
            db.close()
            
            if len(readings) < self.sequence_length + self.prediction_horizon:
                logger.warning(f"Insufficient data for training: {len(readings)} readings")
                return None, None, None
            
            # Convert to DataFrame
            data = []
            for reading in readings:
                data.append({
                    'timestamp': reading.timestamp,
                    'active_energy': reading.active_energy,
                    'active_power': reading.active_power or 0,
                    'voltage_l1': reading.voltage_l1 or 230,
                    'current_l1': reading.current_l1 or 0,
                    'power_factor': reading.power_factor or 1.0,
                    'hour': reading.timestamp.hour,
                    'day_of_week': reading.timestamp.weekday(),
                    'month': reading.timestamp.month,
                    'is_weekend': 1 if reading.timestamp.weekday() >= 5 else 0
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            
            # Resample to hourly data and fill missing values
            df_hourly = df.resample('H').agg({
                'active_energy': 'sum',
                'active_power': 'mean',
                'voltage_l1': 'mean',
                'current_l1': 'mean',
                'power_factor': 'mean',
                'hour': 'first',
                'day_of_week': 'first',
                'month': 'first',
                'is_weekend': 'first'
            }).fillna(method='forward').fillna(0)
            
            # Add weather features (simplified for demo)
            df_hourly['temperature'] = 20 + 10 * np.sin(2 * np.pi * df_hourly.index.hour / 24)
            df_hourly['is_peak_hour'] = ((df_hourly['hour'] >= 17) & (df_hourly['hour'] <= 21)).astype(int)
            
            # Prepare features and target
            feature_columns = [
                'active_power', 'voltage_l1', 'current_l1', 'power_factor',
                'hour', 'day_of_week', 'month', 'is_weekend', 'temperature', 'is_peak_hour'
            ]
            
            features = df_hourly[feature_columns].values
            target = df_hourly['active_energy'].values
            
            # Scale the data
            self.scaler = MinMaxScaler()
            self.feature_scaler = MinMaxScaler()
            
            target_scaled = self.scaler.fit_transform(target.reshape(-1, 1)).flatten()
            features_scaled = self.feature_scaler.fit_transform(features)
            
            # Create sequences
            X, y = self._create_sequences(features_scaled, target_scaled)
            
            logger.info(f"Prepared {len(X)} training sequences")
            return X, y, features_scaled
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            return None, None, None
    
    def _create_sequences(self, features: np.ndarray, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences for LSTM training"""
        X, y = [], []
        
        for i in range(len(target) - self.sequence_length - self.prediction_horizon + 1):
            # Input sequence
            X.append(features[i:(i + self.sequence_length)])
            
            # Target sequence (next 24 hours)
            y.append(target[(i + self.sequence_length):(i + self.sequence_length + self.prediction_horizon)])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """Build LSTM model architecture"""
        model = Sequential([
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(64, return_sequences=True),
            Dropout(0.2),
            BatchNormalization(),
            
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            
            Dense(64, activation='relu'),
            Dropout(0.1),
            
            Dense(32, activation='relu'),
            Dense(self.prediction_horizon, activation='linear')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train_model(self, meter_id: Optional[str] = None) -> bool:
        """Train the LSTM model"""
        try:
            logger.info("Starting LSTM model training...")
            
            # Prepare data
            X, y, _ = self.prepare_data(meter_id)
            
            if X is None:
                logger.error("Failed to prepare training data")
                return False
            
            # Split data
            split_idx = int(len(X) * 0.8)
            X_train, X_val = X[:split_idx], X[split_idx:]
            y_train, y_val = y[:split_idx], y[split_idx:]
            
            # Build model
            self.model = self.build_model((X.shape[1], X.shape[2]))
            
            # Callbacks
            callbacks = [
                EarlyStopping(patience=10, restore_best_weights=True),
                ModelCheckpoint(self.model_path, save_best_only=True)
            ]
            
            # Train model
            history = self.model.fit(
                X_train, y_train,
                validation_data=(X_val, y_val),
                epochs=100,
                batch_size=32,
                callbacks=callbacks,
                verbose=1
            )
            
            # Save scalers
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.feature_scaler, self.feature_scaler_path)
            
            # Evaluate model
            val_predictions = self.model.predict(X_val)
            val_predictions_rescaled = self.scaler.inverse_transform(val_predictions)
            y_val_rescaled = self.scaler.inverse_transform(y_val)
            
            mae = mean_absolute_error(y_val_rescaled.flatten(), val_predictions_rescaled.flatten())
            rmse = np.sqrt(mean_squared_error(y_val_rescaled.flatten(), val_predictions_rescaled.flatten()))
            
            logger.info(f"Model training completed. MAE: {mae:.4f}, RMSE: {rmse:.4f}")
            return True
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return False
    
    def load_model(self) -> bool:
        """Load trained model and scalers"""
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.feature_scaler = joblib.load(self.feature_scaler_path)
                logger.info("Model loaded successfully")
                return True
            else:
                logger.warning("No trained model found")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def predict_consumption(self, meter_id: str) -> Optional[List[Dict]]:
        """Generate energy consumption predictions"""
        try:
            if not self.model:
                if not self.load_model():
                    logger.error("No model available for prediction")
                    return None
            
            # Get recent data for prediction
            db = SessionLocal()
            
            # Get last sequence_length hours of data
            start_time = datetime.utcnow() - timedelta(hours=self.sequence_length)
            readings = db.query(EnergyReading).filter(
                EnergyReading.meter_id == meter_id,
                EnergyReading.timestamp >= start_time
            ).order_by(EnergyReading.timestamp.asc()).all()
            
            if len(readings) < self.sequence_length:
                logger.warning(f"Insufficient recent data for prediction: {len(readings)} readings")
                db.close()
                return None
            
            # Prepare input features
            input_data = []
            for reading in readings[-self.sequence_length:]:
                input_data.append([
                    reading.active_power or 0,
                    reading.voltage_l1 or 230,
                    reading.current_l1 or 0,
                    reading.power_factor or 1.0,
                    reading.timestamp.hour,
                    reading.timestamp.weekday(),
                    reading.timestamp.month,
                    1 if reading.timestamp.weekday() >= 5 else 0,
                    20 + 10 * np.sin(2 * np.pi * reading.timestamp.hour / 24),  # Simplified temperature
                    1 if 17 <= reading.timestamp.hour <= 21 else 0  # Peak hour
                ])
            
            # Scale input data
            input_scaled = self.feature_scaler.transform(np.array(input_data))
            input_sequence = input_scaled.reshape(1, self.sequence_length, -1)
            
            # Make prediction
            prediction_scaled = self.model.predict(input_sequence)
            prediction = self.scaler.inverse_transform(prediction_scaled)
            
            # Create prediction records
            predictions = []
            base_time = datetime.utcnow()
            
            for i, pred_value in enumerate(prediction[0]):
                target_time = base_time + timedelta(hours=i+1)
                
                prediction_record = EnergyPrediction(
                    meter_id=meter_id,
                    prediction_timestamp=base_time,
                    target_timestamp=target_time,
                    predicted_consumption=float(pred_value),
                    confidence_interval_lower=float(pred_value * 0.9),  # Simplified confidence
                    confidence_interval_upper=float(pred_value * 1.1),
                    model_version=self.model_version,
                    model_type="lstm"
                )
                
                db.add(prediction_record)
                
                predictions.append({
                    "target_timestamp": target_time,
                    "predicted_consumption": float(pred_value),
                    "confidence_lower": float(pred_value * 0.9),
                    "confidence_upper": float(pred_value * 1.1)
                })
            
            db.commit()
            db.close()
            
            logger.info(f"Generated {len(predictions)} predictions for meter {meter_id}")
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return None
    
    def generate_predictions(self):
        """Generate predictions for all active meters"""
        try:
            db = SessionLocal()
            
            # Get all active meters
            meters = db.query(SmartMeter).filter(SmartMeter.is_active == True).all()
            
            total_predictions = 0
            for meter in meters:
                predictions = self.predict_consumption(meter.meter_id)
                if predictions:
                    total_predictions += len(predictions)
            
            db.close()
            logger.info(f"Generated predictions for {len(meters)} meters, total {total_predictions} predictions")
            
        except Exception as e:
            logger.error(f"Error generating batch predictions: {e}")
