import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging

logger = setup_logging('risk_manager')

class RiskManager:
    def __init__(self, volatility_analyzer, max_risk_per_trade=0.02, risk_factor=1.5):
        """Initialize the Risk Manager."""
        self.volatility_analyzer = volatility_analyzer
        self.max_risk_per_trade = max_risk_per_trade  # Maximum risk per trade (2% of capital)
        self.risk_factor = risk_factor  # Risk factor multiplier based on volatility
        self.capital = 10000  # Default capital, can be updated

    def set_capital(self, capital):
        """Set the trading capital."""
        self.capital = capital
        logger.info(f"Trading capital set to {self.capital}")

    def calculate_risk(self, symbol, timeframe, limit, exchange_name):
        """Calculate risk based on volatility and market conditions."""
        try:
            volatility = self.volatility_analyzer.get_volatility(symbol, timeframe, limit, exchange_name)
            risk_per_trade = self.capital * self.max_risk_per_trade * (self.risk_factor * volatility)
            logger.info(f"Calculated risk for {symbol}: {risk_per_trade}")
            return risk_per_trade
        except Exception as e:
            logger.error(f"Failed to calculate risk for {symbol}: {str(e)}")
            return self.capital * self.max_risk_per_trade  # Fallback to default risk

    def check_risk_limits(self, trade_size, symbol, timeframe, limit, exchange_name):
        """Check if the trade size is within risk limits."""
        try:
            risk_per_trade = self.calculate_risk(symbol, timeframe, limit, exchange_name)
            if trade_size > risk_per_trade:
                logger.warning(f"Trade size {trade_size} exceeds risk limit {risk_per_trade} for {symbol}")
                return False
            return True
        except Exception as e:
            logger.error(f"Failed to check risk limits for {symbol}: {str(e)}")
            return False

    def calculate_stop_loss(self, entry_price, volatility):
        """Calculate stop-loss based on volatility."""
        try:
            stop_loss_distance = entry_price * (self.risk_factor * volatility)
            stop_loss_price = entry_price - stop_loss_distance if entry_price > 0 else entry_price + stop_loss_distance
            logger.info(f"Calculated stop-loss for entry price {entry_price}: {stop_loss_price}")
            return stop_loss_price
        except Exception as e:
            logger.error(f"Failed to calculate stop-loss: {str(e)}")
            return entry_price * 0.95  # Fallback to 5% below entry price
