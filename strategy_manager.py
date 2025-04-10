from typing import List
from strategies import Strategy
from ml_predictor import predict
from strategy_generator import generate_strategy
from learning.strategy_optimizer import optimize_strategy
import pandas as pd
import logging

def setup_logging():
    logging.basicConfig(
        filename='strategy_manager.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class StrategyManager:
    def __init__(self):
        self.strategies = []
        setup_logging()

    def add_strategy(self, strategy: Strategy):
        self.strategies.append(strategy)
        logging.info(f"Added strategy: {strategy.name}")

    def generate_new_strategy(self, data: pd.DataFrame):
        """Generate and optimize a new strategy."""
        try:
            # Generate a new strategy
            new_strategy = generate_strategy()
            logging.info(f"Generated new strategy: {new_strategy.name}")

            # Optimize the strategy
            data_dict = data.to_dict()
            best_params = optimize_strategy(new_strategy, data_dict)
            new_strategy.params = best_params
            logging.info(f"Optimized strategy {new_strategy.name} with params: {best_params}")

            self.add_strategy(new_strategy)
        except Exception as e:
            logging.error(f"Failed to generate/optimize strategy: {str(e)}")
            raise

    def generate_signals(self, data: pd.DataFrame) -> List[str]:
        """Generate trading signals using strategies and ML predictions."""
        try:
            # Use ML prediction to adjust strategy
            predicted_price = predict(data, model_id=1)
            logging.info(f"Predicted price: {predicted_price}")

            signals = []
            for strategy in self.strategies:
                signal = strategy.generate_signal(predicted_price)
                signals.append(signal)
            logging.info(f"Generated signals: {signals}")
            return signals
        except Exception as e:
            logging.error(f"Failed to generate signals: {str(e)}")
            raise
