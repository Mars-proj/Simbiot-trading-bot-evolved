import pandas as pd
import numpy as np
from logging_setup import setup_logging

logger = setup_logging('features')

def calculate_features(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators as features."""
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

        # Forecast volatility (using GARCH-like approach)
        data['volatility'] = data['price'].pct_change().rolling(window=20).std()
        data['forecasted_volatility'] = data['volatility'].ewm(span=10).mean()

        logger.info("Calculated features for data")
        return data
    except Exception as e:
        logger.error(f"Failed to calculate features: {str(e)}")
        raise

def compute_correlation(data_dict: dict) -> pd.DataFrame:
    """Compute correlation between symbols."""
    try:
        # Create a DataFrame with prices for all symbols
        prices = pd.DataFrame({symbol: df['price'] for symbol, df in data_dict.items()})
        correlation = prices.corr()
        logger.info(f"Computed correlation matrix: {correlation}")
        return correlation
    except Exception as e:
        logger.error(f"Failed to compute correlation: {str(e)}")
        raise

def compute_rsi(prices: pd.Series, period: int) -> pd.Series:
    """Compute RSI for a given period."""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
