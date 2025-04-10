from typing import List
from strategies import Strategy
from ml_predictor import predict
import pandas as pd

class StrategyManager:
    def __init__(self):
        self.strategies = []

    def add_strategy(self, strategy: Strategy):
        self.strategies.append(strategy)

    def generate_signals(self, data: pd.DataFrame) -> List[str]:
        signals = []
        # Use ML prediction to adjust strategy
        predicted_price = predict(data, model_id=1)
        for strategy in self.strategies:
            signal = strategy.generate_signal(predicted_price)
            signals.append(signal)
        return signals
