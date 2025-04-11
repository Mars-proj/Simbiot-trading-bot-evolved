import pandas as pd
import numpy as np
from data_utils import load_order_book
from features import compute_correlation
from logging_setup import setup_logging

logger = setup_logging('market_state_analyzer')

def analyze_market_state(data: pd.DataFrame, exchange: object, symbol: str = 'BTC/USDT', symbols_data: dict = None) -> dict:
    """Analyze the current market state."""
    try:
        # Volatility
        volatility = data['price'].pct_change().std()
        forecasted_volatility = data['forecasted_volatility'].iloc[-1]

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

        # Order book analysis (depth of market)
        order_book = load_order_book(exchange, symbol)
        buy_pressure = sum([bid[1] for bid in order_book['bids']])
        sell_pressure = sum([ask[1] for ask in order_book['asks']])
        order_book_imbalance = (buy_pressure - sell_pressure) / (buy_pressure + sell_pressure) if (buy_pressure + sell_pressure) != 0 else 0

        # Correlation analysis (if multiple symbols provided)
        correlation = None
        if symbols_data:
            correlation = compute_correlation(symbols_data)

        market_state = {
            "volatility": volatility,
            "forecasted_volatility": forecasted_volatility,
            "trend": trend,
            "volume_trend": volume_trend,
            "macd_trend": macd_trend,
            "bb_position": bb_position,
            "has_anomaly": has_anomaly,
            "order_book_imbalance": order_book_imbalance,
            "correlation": correlation.to_dict() if correlation is not None else None
        }
        logger.info(f"Market state: {market_state}")
        return market_state
    except Exception as e:
        logger.error(f"Failed to analyze market state: {str(e)}")
        raise
