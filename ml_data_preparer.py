import pandas as pd
import numpy as np
from features import calculate_features

def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare data for ML model: clean, extract features, normalize."""
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

    return data
