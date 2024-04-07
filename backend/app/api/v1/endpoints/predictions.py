"""
Energy prediction API endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.smart_meter import EnergyPrediction
from app.schemas.energy import EnergyPredictionResponse
from app.ml.lstm_predictor import LSTMPredictor

router = APIRouter()


@router.get("/energy", response_model=List[EnergyPredictionResponse])
async def get_energy_predictions(
    meter_id: Optional[str] = Query(None, description="Filter by meter ID"),
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours to predict"),
    db: Session = Depends(get_db)
):
    """Get energy consumption predictions"""
    
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(hours=hours_ahead)
    
    query = db.query(EnergyPrediction).filter(
        EnergyPrediction.target_timestamp >= start_time,
        EnergyPrediction.target_timestamp <= end_time
    )
    
    if meter_id:
        query = query.filter(EnergyPrediction.meter_id == meter_id)
    
    predictions = query.order_by(EnergyPrediction.target_timestamp.asc()).all()
    
    return predictions


@router.post("/energy/generate")
async def generate_energy_predictions(
    meter_id: Optional[str] = Query(None, description="Generate for specific meter"),
    db: Session = Depends(get_db)
):
    """Generate new energy predictions using LSTM model"""
    
    try:
        predictor = LSTMPredictor()
        
        if meter_id:
            # Generate predictions for specific meter
            predictions = predictor.predict_consumption(meter_id)
            if predictions:
                return {
                    "message": f"Generated {len(predictions)} predictions for meter {meter_id}",
                    "meter_id": meter_id,
                    "predictions_count": len(predictions),
                    "timestamp": datetime.utcnow()
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to generate predictions for meter {meter_id}"
                )
        else:
            # Generate predictions for all meters
            predictor.generate_predictions()
            return {
                "message": "Generated predictions for all active meters",
                "timestamp": datetime.utcnow()
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating predictions: {str(e)}"
        )


@router.get("/energy/accuracy")
async def get_prediction_accuracy(
    meter_id: Optional[str] = Query(None, description="Filter by meter ID"),
    days: int = Query(7, ge=1, le=30, description="Days to analyze"),
    db: Session = Depends(get_db)
):
    """Get prediction accuracy analysis"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(EnergyPrediction).filter(
        EnergyPrediction.prediction_timestamp >= start_date,
        EnergyPrediction.prediction_accuracy.isnot(None)
    )
    
    if meter_id:
        query = query.filter(EnergyPrediction.meter_id == meter_id)
    
    predictions = query.all()
    
    if not predictions:
        return {
            "message": "No accuracy data available for the specified period",
            "analysis_period_days": days,
            "predictions_analyzed": 0
        }
    
    # Calculate accuracy metrics
    accuracies = [p.prediction_accuracy for p in predictions if p.prediction_accuracy]
    
    if accuracies:
        avg_accuracy = sum(accuracies) / len(accuracies)
        min_accuracy = min(accuracies)
        max_accuracy = max(accuracies)
    else:
        avg_accuracy = min_accuracy = max_accuracy = 0
    
    return {
        "analysis_period_days": days,
        "predictions_analyzed": len(predictions),
        "average_accuracy": round(avg_accuracy, 4),
        "minimum_accuracy": round(min_accuracy, 4),
        "maximum_accuracy": round(max_accuracy, 4),
        "accuracy_distribution": {
            "excellent": len([a for a in accuracies if a >= 0.95]),
            "good": len([a for a in accuracies if 0.85 <= a < 0.95]),
            "fair": len([a for a in accuracies if 0.70 <= a < 0.85]),
            "poor": len([a for a in accuracies if a < 0.70])
        }
    }


@router.get("/models/status")
async def get_model_status():
    """Get ML model status and information"""
    
    try:
        predictor = LSTMPredictor()
        model_loaded = predictor.load_model()
        
        return {
            "lstm_model": {
                "loaded": model_loaded,
                "version": predictor.model_version,
                "sequence_length": predictor.sequence_length,
                "prediction_horizon": predictor.prediction_horizon,
                "model_path": predictor.model_path
            },
            "status": "operational" if model_loaded else "model_not_found",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }


@router.post("/models/retrain")
async def retrain_models(
    meter_id: Optional[str] = Query(None, description="Train for specific meter"),
):
    """Trigger model retraining"""
    
    try:
        predictor = LSTMPredictor()
        success = predictor.train_model(meter_id)
        
        if success:
            return {
                "message": "Model retraining completed successfully",
                "meter_id": meter_id,
                "timestamp": datetime.utcnow()
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Model retraining failed"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during model retraining: {str(e)}"
        )
