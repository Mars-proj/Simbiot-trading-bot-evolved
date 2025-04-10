import pandas as pd
import numpy as np
import logging

def setup_logging():
    logging.basicConfig(
        filename='features.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def calculate_features(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators as features."""
    setup_logging()
    try:
        # SMA (Simple Moving Average)
        data['sma_20'] = data['price'].rolling(window=20).mean()
        data['sma_50'] = data['price'].rolling(window=50).mean()

        # RSI (Relative Strength Index)
        data['rsi'] = compute_rsi(data['price'], 14)

        # MACD (Moving Average Convergence Divergence)
        exp1 = data['price'].ewm(span=12, adjust=False).mean()
        exp2 = data['price'].ewm(span=26, adjust=False).mean()
        data['macd'] = exp1 - exp2
        data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        data['macd_hist'] = data['macd'] - data['macd_signal']

        # Bollinger Bands
        data['bb_middle'] = data['price'].rolling(window=20).mean()
        data['bb_std'] = data['price'].rolling(window=20).std()
        data['bb_upper'] = data['bb_middle'] + 2 * data['bb_std']
        data['bb_lower'] = data['bb_middle'] - 2 * data['bb_std']

        # Volume features
        data['volume_sma_20'] = data['volume'].rolling(window=20).mean()
        data['volume_change'] = data['volume'].pct_change()

        # Detect anomalies (price spikes)
        data['price_z_score'] = (data['price'] - data['price'].rolling(window=20).mean()) / data['price'].rolling(window=20).std()
        data['is_anomaly'] = data['price_z_score'].abs() > 3

        logging.info("Calculated features for data")
        return data
    except Exception as e:
        logging.error(f"Failed to calculate features: {str(e)}")
        raise

def compute_rsi(prices: pd.Series, period: int) -> pd.Series:
    """Compute RSI for a given period."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
