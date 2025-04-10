from typing import Dict
from market_state_analyzer import analyze_market_state
from threshold_predictor import predict_threshold
import pandas as pd
from logging_setup import setup_logging

logger = setup_logging('strategies')

class Strategy:
    def __init__(self, name: str, params: Dict):
        self.name = name
        self.params = params
        self.position = None  # Track current position (None, "buy")

    def generate_signal(self, price: float, market_data: pd.DataFrame) -> str:
        """Generate a trading signal with dynamic thresholds based on market conditions and ML prediction."""
        try:
            # Analyze market state to adjust thresholds
            market_state = analyze_market_state(market_data)

            # Predict threshold using ML
            threshold = predict_threshold(market_data, model_id=1)

            # Base thresholds from params
            base_stop_loss = self.params.get('stop_loss', 0.02)
            base_take_profit = self.params.get('take_profit', 0.05)
            strategy_type = self.params.get('strategy_type', 'trend')

            # Adjust thresholds based on volatility
            volatility = market_state['volatility']
            stop_loss = base_stop_loss * (1 + volatility)
            take_profit = base_take_profit * (1 + volatility)

            # Adjust based on market state
            if market_state['trend'] == 'down':
                threshold *= 0.95
            if market_state['macd_trend'] == 'bearish':
                stop_loss *= 0.9

            # Adjust based on strategy type
            if strategy_type == 'countertrend':
                if market_state['bb_position'] == 'overbought':
                    threshold *= 1.05
                elif market_state['bb_position'] == 'oversold':
                    threshold *= 0.95
            elif strategy_type == 'scalping':
                stop_loss *= 0.5
                take_profit *= 0.5

            if self.position is None:
                if price > threshold:
                    self.position = {"type": "buy", "price": price}
                    logger.info(f"Generated buy signal for {self.name} at price {price}")
                    return "buy"
            elif self.position["type"] == "buy":
                current_price = price
                buy_price = self.position["price"]
                profit = (current_price - buy_price) / buy_price
                loss = (buy_price - current_price) / buy_price

                if profit >= take_profit:
                    self.position = None
                    logger.info(f"Generated sell signal for {self.name} at price {current_price} (take-profit)")
                    return "sell"
                elif loss >= stop_loss:
                    self.position = None
                    logger.info(f"Generated sell signal for {self.name} at price {current_price} (stop-loss)")
                    return "sell"
            return "hold"
        except Exception as e:
            logger.error(f"Failed to generate signal for {self.name}: {str(e)}")
            raise

def get_strategy_by_id(strategy_id: int) -> Strategy:
    return Strategy(f"strategy_{strategy_id}", {"stop_loss": 0.02, "take_profit": 0.05, "strategy_type": "trend"})
