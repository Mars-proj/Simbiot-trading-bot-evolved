import pandas as pd
import numpy as np
from data_utils import load_order_book
from features import compute_correlation
from logging_setup import setup_logging

logger = setup_logging('market_state_analyzer')

def analyze_market_state(data: pd.DataFrame, exchange: object, symbol: str = 'BTC/USDT', symbols_data: dict = None) -> dict:
    """Analyze the current market state with dynamic indicator parameters."""
    try:
        # Volatility
        volatility = data['price'].pct_change().std()
        forecasted_volatility = data['forecasted_volatility'].iloc[-1]

        # Dynamic SMA periods based on volatility (higher volatility -> shorter periods)
        sma_short = int(20 * (1 - volatility))  # e.g., 20 to 15
        sma_long = int(50 * (1 - volatility))   # e.g., 50 to 40
        data[f'sma_{sma_short}'] = data['price'].rolling(window=sma_short).mean()
        data[f'sma_{sma_long}'] = data['price'].rolling(window=sma_long).mean()

        # Trend (using SMA crossover)
        trend = 'up' if data[f'sma_{sma_short}'].iloc[-1] > data[f'sma_{sma_long}'].iloc[-1] else 'down'

        # Volume trend
        volume_trend = 'increasing' if data['volume_change'].iloc[-1] > 0 else 'decreasing'

        # Dynamic MACD periods based on volatility
        macd_fast = int(12 * (1 - volatility))  # e.g., 12 to 9
        macd_slow = int(26 * (1 - volatility))  # e.g., 26 to 20
        macd_signal = int(9 * (1 - volatility))  # e.g., 9 to 7
        data['ema_fast'] = data['price'].ewm(span=macd_fast, adjust=False).mean()
        data['ema_slow'] = data['price'].ewm(span=macd_slow, adjust=False).mean()
        data['macd'] = data['ema_fast'] - data['ema_slow']
        data['macd_signal'] = data['macd'].ewm(span=macd_signal, adjust=False).mean()

        # MACD trend
        macd_trend = 'bullish' if data['macd'].iloc[-1] > data['macd_signal'].iloc[-1] else 'bearish'

        # Dynamic Bollinger Bands period based on volatility
        bb_period = int(20 * (1 - volatility))  # e.g., 20 to 15
        data['bb_middle'] = data['price'].rolling(window=bb_period).mean()
        data['bb_std'] = data['price'].rolling(window=bb_period).std()
        data['bb_upper'] = data['bb_middle'] + 2 * data['bb_std']
        data['bb_lower'] = data['bb_middle'] - 2 * data['bb_std']

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
        order_book = load_order_book(exchange, symbol, {'volatility': volatility})
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
