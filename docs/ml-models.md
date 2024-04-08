# Machine Learning Models Guide

## Overview

The Smart Grid IoT Analytics platform uses advanced machine learning models for energy prediction, renewable forecasting, and pricing optimization. This guide covers the implementation, training, and deployment of these models.

## LSTM Energy Prediction Model

### Architecture

The LSTM (Long Short-Term Memory) model is designed for time-series prediction of energy consumption:

```python
model = Sequential([
    LSTM(128, return_sequences=True, input_shape=(168, 10)),
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
    Dense(24, activation='linear')  # 24-hour prediction
])
```

### Features

**Input Features (10 dimensions):**
- Active power (kW)
- Voltage L1 (V)
- Current L1 (A)
- Power factor
- Hour of day (0-23)
- Day of week (0-6)
- Month (1-12)
- Is weekend (0/1)
- Temperature (°C)
- Is peak hour (0/1)

**Sequence Length:** 168 hours (7 days)
**Prediction Horizon:** 24 hours

### Training Process

1. **Data Preparation**
   ```python
   # Resample to hourly data
   df_hourly = df.resample('H').agg({
       'active_energy': 'sum',
       'active_power': 'mean',
       # ... other features
   })
   
   # Feature scaling
   scaler = MinMaxScaler()
   features_scaled = scaler.fit_transform(features)
   ```

2. **Sequence Creation**
   ```python
   def create_sequences(features, target, sequence_length=168):
       X, y = [], []
       for i in range(len(target) - sequence_length - 24 + 1):
           X.append(features[i:(i + sequence_length)])
           y.append(target[(i + sequence_length):(i + sequence_length + 24)])
       return np.array(X), np.array(y)
   ```

3. **Model Training**
   ```python
   model.compile(
       optimizer=Adam(learning_rate=0.001),
       loss='mse',
       metrics=['mae']
   )
   
   history = model.fit(
       X_train, y_train,
       validation_data=(X_val, y_val),
       epochs=100,
       batch_size=32,
       callbacks=[EarlyStopping(patience=10)]
   )
   ```

### Performance Metrics

- **MAE (Mean Absolute Error)**: < 5% of average consumption
- **RMSE (Root Mean Square Error)**: < 8% of average consumption
- **MAPE (Mean Absolute Percentage Error)**: < 10%

## Renewable Energy Forecasting

### Solar Power Prediction

**Model Type:** Random Forest Regressor
**Features:**
- Solar irradiance (W/m²)
- Temperature (°C)
- Cloud cover (%)
- Hour of day
- Day of year
- Panel specifications

```python
from sklearn.ensemble import RandomForestRegressor

solar_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    random_state=42
)
```

### Wind Power Prediction

**Model Type:** Gradient Boosting Regressor
**Features:**
- Wind speed (m/s)
- Wind direction (degrees)
- Temperature (°C)
- Pressure (hPa)
- Turbine specifications

```python
from sklearn.ensemble import GradientBoostingRegressor

wind_model = GradientBoostingRegressor(
    n_estimators=150,
    learning_rate=0.1,
    max_depth=8,
    random_state=42
)
```

## Dynamic Pricing Optimization

### Optimization Algorithm

The pricing optimization uses a multi-objective approach:

```python
def optimize_pricing(demand_forecast, supply_forecast, market_conditions):
    # Objective function
    def objective(price):
        revenue = price * demand_forecast
        stability = grid_stability_score(price, demand_forecast)
        efficiency = market_efficiency(price, supply_forecast)
        
        return -(revenue + stability + efficiency)  # Minimize negative
    
    # Constraints
    constraints = [
        {'type': 'ineq', 'fun': lambda x: x - min_price},
        {'type': 'ineq', 'fun': lambda x: max_price - x}
    ]
    
    result = minimize(objective, initial_price, constraints=constraints)
    return result.x[0]
```

### Factors Considered

1. **Supply-Demand Balance**
   - Real-time demand predictions
   - Available generation capacity
   - Renewable energy availability

2. **Market Conditions**
   - Wholesale electricity prices
   - Transmission congestion
   - Grid frequency stability

3. **Time-of-Use Patterns**
   - Peak hour premiums
   - Off-peak discounts
   - Seasonal adjustments

## Model Training Pipeline

### Automated Retraining

```python
class ModelTrainer:
    def __init__(self):
        self.lstm_predictor = LSTMPredictor()
        self.renewable_forecaster = RenewableForecaster()
    
    def retrain_lstm_model(self):
        # Get latest data
        data = self.get_training_data()
        
        # Train model
        success = self.lstm_predictor.train_model()
        
        if success:
            # Evaluate performance
            metrics = self.evaluate_model()
            
            # Deploy if performance is acceptable
            if metrics['mae'] < threshold:
                self.deploy_model()
```

### Scheduled Training

Models are retrained automatically:
- **LSTM Model**: Daily at 2:00 AM
- **Renewable Models**: Weekly on Sundays
- **Pricing Model**: Continuously updated

## Model Evaluation

### Cross-Validation

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=tscv, scoring='neg_mean_absolute_error')
```

### Performance Monitoring

```python
def calculate_accuracy_metrics(predictions, actuals):
    mae = mean_absolute_error(actuals, predictions)
    rmse = np.sqrt(mean_squared_error(actuals, predictions))
    mape = np.mean(np.abs((actuals - predictions) / actuals)) * 100
    
    return {
        'mae': mae,
        'rmse': rmse,
        'mape': mape,
        'r2': r2_score(actuals, predictions)
    }
```

## Feature Engineering

### Time-Based Features

```python
def create_time_features(df):
    df['hour'] = df.index.hour
    df['day_of_week'] = df.index.dayofweek
    df['month'] = df.index.month
    df['quarter'] = df.index.quarter
    df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
    df['is_peak_hour'] = ((df.index.hour >= 17) & (df.index.hour <= 21)).astype(int)
    return df
```

### Weather Features

```python
def add_weather_features(df, weather_data):
    df['temperature'] = weather_data['temperature']
    df['humidity'] = weather_data['humidity']
    df['wind_speed'] = weather_data['wind_speed']
    df['solar_irradiance'] = calculate_solar_irradiance(weather_data)
    return df
```

## Model Deployment

### Model Serving

```python
class ModelServer:
    def __init__(self):
        self.lstm_model = self.load_lstm_model()
        self.renewable_models = self.load_renewable_models()
    
    def predict_energy_consumption(self, meter_id, hours_ahead=24):
        # Prepare input data
        input_data = self.prepare_input_data(meter_id)
        
        # Make prediction
        prediction = self.lstm_model.predict(input_data)
        
        # Post-process results
        return self.post_process_prediction(prediction)
```

### API Integration

```python
@router.post("/predictions/generate")
async def generate_predictions():
    model_server = ModelServer()
    predictions = model_server.generate_all_predictions()
    return {"predictions": predictions}
```

## Hyperparameter Tuning

### Grid Search for LSTM

```python
param_grid = {
    'lstm_units': [64, 128, 256],
    'dropout_rate': [0.1, 0.2, 0.3],
    'learning_rate': [0.001, 0.01, 0.1],
    'batch_size': [16, 32, 64]
}

best_params = grid_search_lstm(param_grid, X_train, y_train)
```

### Bayesian Optimization

```python
from skopt import gp_minimize

def objective(params):
    model = build_model(params)
    score = cross_validate(model, X, y)
    return -score  # Minimize negative score

result = gp_minimize(objective, space, n_calls=50)
```

## Data Quality and Preprocessing

### Outlier Detection

```python
def detect_outliers(data, threshold=3):
    z_scores = np.abs(stats.zscore(data))
    return z_scores > threshold

def handle_outliers(df, method='clip'):
    if method == 'clip':
        df = df.clip(lower=df.quantile(0.01), upper=df.quantile(0.99))
    elif method == 'remove':
        df = df[~detect_outliers(df)]
    return df
```

### Missing Data Handling

```python
def handle_missing_data(df):
    # Forward fill for short gaps
    df = df.fillna(method='ffill', limit=3)
    
    # Interpolation for longer gaps
    df = df.interpolate(method='time')
    
    # Remove remaining NaN values
    df = df.dropna()
    
    return df
```

## Model Interpretability

### Feature Importance

```python
def plot_feature_importance(model, feature_names):
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(importance)), importance[indices])
    plt.xticks(range(len(importance)), [feature_names[i] for i in indices], rotation=45)
    plt.title('Feature Importance')
    plt.show()
```

### SHAP Analysis

```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test, feature_names=feature_names)
```

## Best Practices

1. **Data Quality**
   - Regular data validation
   - Outlier detection and handling
   - Missing data imputation

2. **Model Validation**
   - Time-series cross-validation
   - Out-of-sample testing
   - Performance monitoring

3. **Feature Engineering**
   - Domain knowledge integration
   - Temporal feature creation
   - Weather data incorporation

4. **Model Maintenance**
   - Regular retraining
   - Performance monitoring
   - A/B testing for improvements

5. **Deployment**
   - Model versioning
   - Gradual rollout
   - Fallback mechanisms
