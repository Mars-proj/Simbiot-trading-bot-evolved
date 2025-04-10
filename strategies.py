from typing import Dict

class Strategy:
    def __init__(self, name: str, params: Dict):
        self.name = name
        self.params = params
        self.position = None  # Track current position (None, "buy")

    def generate_signal(self, price: float) -> str:
        """Generate a trading signal with stop-loss and take-profit."""
        threshold = self.params.get('threshold', 10000)
        stop_loss = self.params.get('stop_loss', 0.02)
        take_profit = self.params.get('take_profit', 0.05)

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
