import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from utils.performance_tracker import PerformanceTracker
from analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('trade_executor')

class TradeExecutor:
    def __init__(self, market_state: dict, market_data):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data=market_data)
        self.min_trade_amount = 10.0  # Минимальная сумма сделки в долларах
        self.commission_rate = 0.001  # Комиссия 0.1%

    def execute_trade(self, symbol: str, side: str, klines: list, entry_price: float, stop_loss: float, account_balance: float, exchange_name: str = 'mexc') -> dict:
        """Execute a trade with dynamic stop-loss and take-profit."""
        try:
            # Проверяем минимальную сумму сделки
            trade_amount = max(self.min_trade_amount + (self.min_trade_amount * self.commission_rate), account_balance * 0.01)  # 1% от баланса, но не менее минимальной суммы
            if trade_amount > account_balance:
                logger.warning(f"Insufficient balance for trade: {trade_amount} > {account_balance}")
                return {}

            # Динамически рассчитываем тейк-профит на основе волатильности
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            take_profit_percentage = 0.10 * (1 + symbol_volatility)  # Базовый тейк-профит 10%, корректируется на волатильность
            take_profit = entry_price * (1 + take_profit_percentage if side == 'buy' else 1 - take_profit_percentage)

            # Симулируем выполнение сделки
            trade = {
                'symbol': symbol,
                'side': side,
                'entry_price': entry_price,
                'amount': trade_amount,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'timestamp': klines[-1]['timestamp']
            }

            # Логируем сделку
            logger.info(f"Executed trade: {trade}")
            self.performance_tracker.record_request()

            return trade
        except Exception as e:
            logger.error(f"Failed to execute trade for {symbol}: {str(e)}")
            self.performance_tracker.record_error()
            raise
