import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib
import os
from logging_setup import setup_logging

logger = setup_logging('ml_model_trainer')

def train_model(model_id: int, data: pd.DataFrame) -> None:
    """Train an LSTM model and save it."""
    try:
        # Prepare data for LSTM
        from ml_data_preparer import prepare_data
        X, y = prepare_data(data)

        # Build LSTM model
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
            Dropout(0.2),
            LSTM(50),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')

        # Train model
        model.fit(X, y, epochs=10, batch_size=32, verbose=1)

        # Save model
        model_path = f"models/model_{model_id}.h5"
        os.makedirs("models", exist_ok=True)
        model.save(model_path)
        logger.info(f"Model {model_id} trained and saved to {model_path}")
    except Exception as e:
        logger.error(f"Failed to train model {model_id}: {str(e)}")
        raise
