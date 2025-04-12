import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker
from trading_bot.analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('risk_calculator')

class RiskCalculator:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)
        self.min_trade_amount = 10.0  # Минимальная сумма сделки в долларах
        self.commission_rate = 0.001  # Комиссия 0.1%

    def calculate_risk(self, symbol: str, account_balance: float, entry_price: float, exchange_name: str = 'mexc') -> dict:
        """Calculate risk parameters dynamically based on market conditions."""
        try:
            # Получаем волатильность символа
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)

            # Динамически рассчитываем риск на основе волатильности
            risk_percentage = 0.01 * (1 + symbol_volatility)  # Базовый риск 1%, корректируется на волатильность
            position_size = account_balance * risk_percentage

            # Учитываем минимальную сумму сделки
            position_size = max(self.min_trade_amount + (self.min_trade_amount * self.commission_rate), position_size)

            # Динамически рассчитываем стоп-лосс и тейк-профит
            stop_loss_percentage = 0.05 * (1 + symbol_volatility)  # Базовый стоп-лосс 5%
            take_profit_percentage = 0.10 * (1 + symbol_volatility)  # Базовый тейк-профит 10%

            risk_params = {
                'position_size': min(position_size, account_balance),  # Не превышаем баланс
                'stop_loss_percentage': stop_loss_percentage,
                'take_profit_percentage': take_profit_percentage,
                'risk_percentage': risk_percentage
            }

            logger.info(f"Calculated risk parameters for {symbol}: {risk_params}")
            return risk_params
        except Exception as e:
            logger.error(f"Failed to calculate risk for {symbol}: {str(e)}")
            raise
