import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
from logging_setup import setup_logging

logger = setup_logging('ml_predictor')

def predict(data: pd.DataFrame, model_id: int) -> float:
    """Make a prediction using an LSTM model."""
    try:
        # Load model
        model_path = f"models/model_{model_id}.h5"
        model = load_model(model_path)

        # Prepare data
        from ml_data_preparer import prepare_data
        X, _ = prepare_data(data)
        X = X[-1:]  # Use the last sequence for prediction

        # Predict
        prediction = model.predict(X, verbose=0)[0][0]
        logger.info(f"Prediction made: {prediction}")
        return float(prediction)
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise
