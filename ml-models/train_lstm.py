"""
Train LSTM Energy Prediction Model
Trains the LSTM model using historical energy consumption data
"""

import os
import sys

# Add backend to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.ml.lstm_predictor import LSTMPredictor
from app.core.config import settings

def main():
    """Train the LSTM model"""
    print("🤖 Starting LSTM Model Training...")
    print(f"   Sequence Length: {settings.LSTM_SEQUENCE_LENGTH} hours (7 days)")
    print(f"   Prediction Horizon: {settings.PREDICTION_HORIZON_HOURS} hours (1 day)")
    print()

    # Initialize predictor
    predictor = LSTMPredictor()

    # Override model directory to use local path
    local_model_dir = os.path.join(os.path.dirname(__file__), 'lstm')
    predictor.model_dir = local_model_dir
    predictor.model_path = f"{local_model_dir}/lstm_energy_model.keras"
    predictor.scaler_path = f"{local_model_dir}/energy_scaler.pkl"
    predictor.feature_scaler_path = f"{local_model_dir}/feature_scaler.pkl"

    # Ensure model directory exists
    os.makedirs(local_model_dir, exist_ok=True)
    print(f"📁 Model directory: {local_model_dir}")
    print()

    # Train model (using all meters' data)
    print("📊 Training model with all meters' data...")
    success = predictor.train_model(meter_id=None)

    if success:
        print("\n✅ Model training completed successfully!")
        print(f"   Model saved to: {predictor.model_path}")
        print(f"   Scaler saved to: {predictor.scaler_path}")
        print(f"   Feature scaler saved to: {predictor.feature_scaler_path}")

        # Test loading the model
        print("\n🔍 Verifying model can be loaded...")
        if predictor.load_model():
            print("✅ Model loaded successfully!")
        else:
            print("❌ Failed to load model")
            sys.exit(1)
    else:
        print("\n❌ Model training failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

