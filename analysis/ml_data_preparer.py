import pandas as pd
import numpy as np
from features import calculate_features
from logging_setup import setup_logging

logger = setup_logging('ml_data_preparer')

def prepare_data(data: pd.DataFrame, time_steps: int = 60) -> tuple:
    """Prepare data for ML model: clean, extract features, normalize, create sequences for LSTM."""
    try:
        # Remove NaNs
        data = data.dropna()

        # Extract features (using features.py)
        data = calculate_features(data)

        # Add more features: price change, volatility
        data['price_change'] = data['price'].pct_change()
        data['volatility'] = data['price'].rolling(window=20).std()

        # Remove NaNs after feature extraction
        data = data.dropna()

        # Normalize numerical columns
        numerical_cols = ['price', 'sma_20', 'rsi', 'price_change', 'volatility']
        for col in numerical_cols:
            data[col] = (data[col] - data[col].mean()) / data[col].std()

        # Create sequences for LSTM
        X, y = [], []
        for i in range(len(data) - time_steps):
            X.append(data[numerical_cols].iloc[i:i + time_steps].values)
            y.append(data['price'].iloc[i + time_steps])
        X = np.array(X)
        y = np.array(y)

        logger.info(f"Prepared {len(X)} sequences for LSTM training")
        return X, y
    except Exception as e:
        logger.error(f"Failed to prepare data: {str(e)}")
        raise
