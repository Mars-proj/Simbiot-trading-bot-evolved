import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os
from logging_setup import setup_logging

logger = setup_logging('threshold_predictor')

def train_threshold_predictor(data: pd.DataFrame, model_id: int) -> None:
    """Train a model to predict optimal thresholds."""
    try:
        # Prepare features for threshold prediction
        X = data[['volatility', 'rsi', 'macd', 'price_change']]
        y = data['price'].shift(-1)  # Use future price as a proxy for threshold
        X = X[:-1]
        y = y[:-1]

        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Save model
        model_path = f"models/threshold_model_{model_id}.joblib"
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, model_path)
        logger.info(f"Threshold predictor {model_id} trained and saved to {model_path}")
    except Exception as e:
        logger.error(f"Failed to train threshold predictor {model_id}: {str(e)}")
        raise

def predict_threshold(data: pd.DataFrame, model_id: int) -> float:
    """Predict an optimal threshold using ML."""
    try:
        # Load model
        model_path = f"models/threshold_model_{model_id}.joblib"
        model = joblib.load(model_path)

        # Prepare features
        X = data[['volatility', 'rsi', 'macd', 'price_change']]
        X = X.iloc[-1:]  # Use the last row for prediction

        # Predict
        threshold = model.predict(X)[0]
        logger.info(f"Predicted threshold: {threshold}")
        return float(threshold)
    except Exception as e:
        logger.error(f"Failed to predict threshold: {str(e)}")
        raise
