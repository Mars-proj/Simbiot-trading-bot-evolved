import pandas as pd
from logging_setup import setup_logging

logger = setup_logging('risk_manager')

class RiskManager:
    def __init__(self, exchange: object, market_state: dict):
        # Dynamic max loss based on market state and balance
        try:
            balance = exchange.fetch_balance()
            usdt_balance = balance['free'].get('USDT', 0.0)
            volatility = market_state['volatility']
            # Lower max loss in high volatility markets
            volatility_factor = max(0.1, min(1.0, 1.0 / (volatility + 0.01)))
            self.max_loss = usdt_balance * 0.05 * volatility_factor  # 5% of balance, scaled by volatility
            self.current_loss = 0.0
            logger.info(f"Initialized RiskManager with dynamic max_loss: {self.max_loss}")
        except Exception as e:
            logger.error(f"Failed to initialize RiskManager: {str(e)}")
            raise

    def check_risk(self, trade: dict, market_data: pd.DataFrame) -> bool:
        """Check if a trade is within risk limits."""
        try:
            # Calculate trade value
            trade_value = trade['price'] * trade['amount']

            # Simple VaR calculation (Value at Risk)
            volatility = market_data['price'].pct_change().std()
            var_95 = trade_value * 1.65 * volatility  # 95% confidence level
            potential_loss = trade_value + var_95

            if self.current_loss + potential_loss > self.max_loss:
                logger.warning(f"Trade rejected: exceeds max loss limit. Current loss: {self.current_loss}, Potential loss: {potential_loss}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to check risk: {str(e)}")
            raise

    def update_loss(self, trade_result: float):
        """Update the current loss based on trade result."""
        try:
            self.current_loss += trade_result
            if self.current_loss < 0:
                self.current_loss = 0.0  # Reset if profit
            logger.info(f"Updated current loss: {self.current_loss}")
        except Exception as e:
            logger.error(f"Failed to update loss: {str(e)}")
            raise
