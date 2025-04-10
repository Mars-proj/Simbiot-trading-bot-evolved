from typing import List
from strategies import Strategy
from ml_predictor import predict
from market_state_analyzer import analyze_market_state
from symbol_filter import filter_symbols
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
    def __init__(self, exchange_id: str):
        self.strategies = []
        self.exchange_id = exchange_id
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

    def filter_symbols(self, symbols: List[str]) -> List[str]:
        """Filter symbols based on market conditions."""
        try:
            filtered = filter_symbols(self.exchange_id, symbols, min_volume=1000, min_liquidity=0.01, max_volatility=0.05)
            logging.info(f"Filtered symbols: {filtered}")
            return filtered
        except Exception as e:
            logging.error(f"Failed to filter symbols: {str(e)}")
            raise

    def generate_signals(self, data: pd.DataFrame) -> List[str]:
        """Generate trading signals using strategies, ML predictions, and market analysis."""
        try:
            # Use ML prediction to adjust strategy
            predicted_price = predict(data, model_id=1)
            logging.info(f"Predicted price: {predicted_price}")

            # Analyze market state
            market_state = analyze_market_state(data)
            logging.info(f"Market state: {market_state}")

            signals = []
            for strategy in self.strategies:
                # Adjust signal based on market state
                signal = strategy.generate_signal(predicted_price)
                if market_state['has_anomaly']:
                    signal = "hold"  # Avoid trading during anomalies
                elif market_state['bb_position'] == 'overbought' and signal == "buy":
                    signal = "hold"  # Avoid buying in overbought conditions
                elif market_state['bb_position'] == 'oversold' and signal == "sell":
                    signal = "hold"  # Avoid selling in oversold conditions
                signals.append(signal)
            logging.info(f"Generated signals: {signals}")
            return signals
        except Exception as e:
            logging.error(f"Failed to generate signals: {str(e)}")
            raise
