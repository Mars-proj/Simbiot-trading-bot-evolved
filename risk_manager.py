from typing import Dict
from market_state_analyzer import analyze_market_state
import pandas as pd
from logging_setup import setup_logging

logger = setup_logging('risk_manager')

class RiskManager:
    def __init__(self, base_max_loss: float):
        self.base_max_loss = base_max_loss
        self.current_loss = 0.0

    def check_risk(self, trade: Dict, market_data: pd.DataFrame) -> bool:
        """Check if a trade exceeds risk limits, adjusting dynamically."""
        try:
            # Analyze market state to adjust risk limits
            market_state = analyze_market_state(market_data)
            volatility = market_state['volatility']

            # Adjust max loss based on volatility
            max_loss = self.base_max_loss * (1 + volatility)  # Increase risk tolerance in volatile markets
            if market_state['trend'] == 'down':
                max_loss *= 0.8  # Reduce risk in downtrend

            # Calculate potential loss
            potential_loss = trade['amount'] * trade['price'] * 0.01  # 1% potential loss
            self.current_loss += potential_loss

            can_trade = self.current_loss <= max_loss
            logger.info(f"Risk check: current_loss={self.current_loss}, max_loss={max_loss}, can_trade={can_trade}")
            return can_trade
        except Exception as e:
            logger.error(f"Risk check failed: {str(e)}")
            raise
