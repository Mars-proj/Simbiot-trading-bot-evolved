import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('ml_strategy')

class MLStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state, market_data)
        self.min_order_size = 0.001  # Минимальный размер ордера (жёсткий порог)

    async def generate_signal(self, symbol: str, timeframe: str, limit: int, exchange_name: str, predictions=None, volatility=None) -> str:
        """Generate a trading signal using ML predictions with dynamic thresholds."""
        try:
            if not predictions:
                logger.warning(f"No predictions for {symbol}, returning hold signal")
                return 'hold'

            prediction = predictions[0] if isinstance(predictions, list) and predictions else 0.5

            # Динамический порог на основе волатильности
            buy_threshold = 0.5 + (volatility * 0.2) if volatility else 0.6  # Чем выше волатильность, тем выше порог для покупки
            sell_threshold = 0.5 - (volatility * 0.2) if volatility else 0.4  # Чем выше волатильность, тем ниже порог для продажи

            buy_threshold = max(0.55, min(0.75, buy_threshold))
            sell_threshold = max(0.25, min(0.45, sell_threshold))

            signal = 'hold'
            if prediction > buy_threshold:
                signal = 'buy'
            elif prediction < sell_threshold:
                signal = 'sell'

            # Проверка минимального размера ордера
            if signal != 'hold':
                klines = await self.market_data.get_klines(symbol, timeframe, 1, exchange_name)
                if not klines:
                    logger.warning(f"No klines data for {symbol}, skipping trade")
                    return 'hold'
                current_price = klines[-1]['close']
                quantity = 0.1 / current_price  # Пример расчёта количества (10% от баланса)
                if quantity < self.min_order_size:
                    logger.warning(f"Order size {quantity} for {symbol} is below minimum {self.min_order_size}, skipping trade")
                    signal = 'hold'

            logger.info(f"ML signal for {symbol}: {signal}, prediction={prediction}, buy_threshold={buy_threshold}, sell_threshold={sell_threshold}")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate ML signal for {symbol}: {str(e)}")
            return 'hold'
