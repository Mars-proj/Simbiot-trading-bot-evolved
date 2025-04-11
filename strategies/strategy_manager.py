from typing import List
from strategies import Strategy
from ml_predictor import predict
from market_state_analyzer import analyze_market_state
from symbol_filter import filter_symbols
from strategy_generator import generate_strategy
from learning.strategy_optimizer import optimize_strategy
from risk_manager import RiskManager
import pandas as pd
from logging_setup import setup_logging

logger = setup_logging('strategy_manager')

class StrategyManager:
    def __init__(self, exchange_id: str):
        self.strategies = []
        self.exchange_id = exchange_id
        self.risk_manager = RiskManager(base_max_loss=1000.0)  # Will be made dynamic in risk_manager.py

    def add_strategy(self, strategy: Strategy):
        self.strategies.append(strategy)
        logger.info(f"Added strategy: {strategy.name}")

    def generate_new_strategy(self, data: pd.DataFrame):
        """Generate and optimize a new strategy."""
        try:
            # Generate a new strategy
            new_strategy = generate_strategy()
            logger.info(f"Generated new strategy: {new_strategy.name}")

            # Optimize the strategy
            data_dict = data.to_dict()
            best_params = optimize_strategy(new_strategy, data_dict)
            new_strategy.params = best_params
            logger.info(f"Optimized strategy {new_strategy.name} with params: {best_params}")

            self.add_strategy(new_strategy)
        except Exception as e:
            logger.error(f"Failed to generate/optimize strategy: {str(e)}")
            raise

    def filter_symbols(self, symbols: List[str], exchange: object, market_state: dict) -> List[str]:
        """Filter symbols based on market conditions with dynamic parameters."""
        try:
            # Dynamic parameters based on market state
            volatility = market_state['volatility']
            order_book_imbalance = market_state['order_book_imbalance']

            # Adjust min_volume based on volatility (higher volatility -> higher volume requirement)
            min_volume = 500.0 * (1 + volatility)

            # Adjust min_liquidity based on order book imbalance (higher imbalance -> stricter liquidity)
            min_liquidity = 0.01 * (1 + abs(order_book_imbalance))

            # Adjust max_volatility based on market state (allow higher volatility if market is trending)
            max_volatility = 0.05 if market_state['trend'] == 'up' else 0.03

            filtered = filter_symbols(exchange, symbols, min_volume=min_volume, min_liquidity=min_liquidity, max_volatility=max_volatility)
            logger.info(f"Filtered symbols: {filtered}")
            return filtered
        except Exception as e:
            logger.error(f"Failed to filter symbols: {str(e)}")
            raise

    def generate_signals(self, data: pd.DataFrame, exchange: object) -> List[str]:
        """Generate trading signals using strategies, ML predictions, and market analysis."""
        try:
            # Analyze market state to determine model_id dynamically
            market_state = analyze_market_state(data, exchange)
            # Use a simpler model for high volatility, more complex for stable markets
            model_id = 1 if market_state['volatility'] > 0.03 else 2
            logger.info(f"Selected model_id: {model_id} based on volatility: {market_state['volatility']}")

            # Use ML prediction to adjust strategy
            predicted_price = predict(data, model_id=model_id)
            logger.info(f"Predicted price: {predicted_price}")

            # Analyze market state
            market_state = analyze_market_state(data, exchange)
            logger.info(f"Market state: {market_state}")

            signals = []
            for strategy in self.strategies:
                # Adjust signal based on market state
                signal = strategy.generate_signal(predicted_price, data)
                if market_state['has_anomaly']:
                    signal = "hold"  # Avoid trading during anomalies
                elif market_state['bb_position'] == 'overbought' and signal == "buy":
                    signal = "hold"  # Avoid buying in overbought conditions
                elif market_state['bb_position'] == 'oversold' and signal == "sell":
                    signal = "hold"  # Avoid selling in oversold conditions

                # Check risk before trading (amount will be set in core.py)
                if signal in ["buy", "sell"]:
                    trade = {"symbol": "BTC/USDT", "price": predicted_price}
                    if not self.risk_manager.check_risk(trade, data):
                        signal = "hold"  # Skip trade if risk limit exceeded
                        logger.info(f"Trade skipped due to risk limit: {trade}")

                signals.append(signal)
            logger.info(f"Generated signals: {signals}")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate signals: {str(e)}")
            raise
