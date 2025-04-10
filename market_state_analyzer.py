import pandas as pd
import numpy as np
import logging

def setup_logging():
    logging.basicConfig(
        filename='market_state_analyzer.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def analyze_market_state(data: pd.DataFrame) -> dict:
    """Analyze the current market state."""
    setup_logging()
    try:
        # Volatility
        volatility = data['price'].pct_change().std()

        # Trend (using SMA crossover)
        trend = 'up' if data['sma_20'].iloc[-1] > data['sma_50'].iloc[-1] else 'down'

        # Volume trend
        volume_trend = 'increasing' if data['volume_change'].iloc[-1] > 0 else 'decreasing'

        # MACD trend
        macd_trend = 'bullish' if data['macd'].iloc[-1] > data['macd_signal'].iloc[-1] else 'bearish'

        # Bollinger Bands position
        if data['price'].iloc[-1] > data['bb_upper'].iloc[-1]:
            bb_position = 'overbought'
        elif data['price'].iloc[-1] < data['bb_lower'].iloc[-1]:
            bb_position = 'oversold'
        else:
            bb_position = 'neutral'

        # Anomalies
        has_anomaly = data['is_anomaly'].iloc[-1]

        market_state = {
            "volatility": volatility,
            "trend": trend,
            "volume_trend": volume_trend,
            "macd_trend": macd_trend,
            "bb_position": bb_position,
            "has_anomaly": has_anomaly
        }
        logging.info(f"Market state: {market_state}")
        return market_state
    except Exception as e:
        logging.error(f"Failed to analyze market state: {str(e)}")
        raise
