from typing import Dict
from market_state_analyzer import analyze_market_state
import pandas as pd

class Strategy:
    def __init__(self, name: str, params: Dict):
        self.name = name
        self.params = params
        self.position = None  # Track current position (None, "buy")

    def generate_signal(self, price: float, market_data: pd.DataFrame) -> str:
        """Generate a trading signal with dynamic thresholds based on market conditions."""
        # Analyze market state to adjust thresholds
        market_state = analyze_market_state(market_data)

        # Base thresholds from params
        base_threshold = self.params.get('threshold', 10000)
        base_stop_loss = self.params.get('stop_loss', 0.02)
        base_take_profit = self.params.get('take_profit', 0.05)

        # Adjust thresholds based on volatility
        volatility = market_state['volatility']
        threshold = base_threshold * (1 + volatility)  # Increase threshold in volatile markets
        stop_loss = base_stop_loss * (1 + volatility)  # Wider stop-loss in volatile markets
        take_profit = base_take_profit * (1 + volatility)  # Wider take-profit in volatile markets

        # Adjust based on market state
        if market_state['trend'] == 'down':
            threshold *= 0.95  # Lower threshold in downtrend
        if market_state['macd_trend'] == 'bearish':
            stop_loss *= 0.9  # Tighter stop-loss in bearish MACD

        if self.position is None:
            if price > threshold:
                self.position = {"type": "buy", "price": price}
                return "buy"
        elif self.position["type"] == "buy":
            current_price = price
            buy_price = self.position["price"]
            profit = (current_price - buy_price) / buy_price
            loss = (buy_price - current_price) / buy_price

            if profit >= take_profit:
                self.position = None
                return "sell"
            elif loss >= stop_loss:
                self.position = None
                return "sell"
        return "hold"

def get_strategy_by_id(strategy_id: int) -> Strategy:
    return Strategy(f"strategy_{strategy_id}", {"threshold": 10000, "stop_loss": 0.02, "take_profit": 0.05})
