import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('arbitrage_strategy')

class ArbitrageStrategy(Strategy):
    def __init__(self, market_state: dict, market_data=None):
        super().__init__(market_state, market_data=market_data)
        self.price_diff_threshold = 0.05  # Порог разницы цен для арбитража (5%)

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using arbitrage opportunities."""
        try:
            # Получаем доступные биржи
            exchanges = self.market_data.get_available_exchanges()
            if len(exchanges) < 2:
                logger.warning("Not enough exchanges for arbitrage")
                return "hold"

            # Получаем цены с разных бирж
            tasks = [self.market_data.get_klines(symbol, timeframe, 1, exchange) for exchange in exchanges]
            klines_list = await asyncio.gather(*tasks, return_exceptions=True)

            prices = {}
            for exchange, klines in zip(exchanges, klines_list):
                if isinstance(klines, Exception) or not klines:
                    logger.warning(f"No data for {symbol} on {exchange}")
                    continue
                prices[exchange] = klines[-1]['close']

            if len(prices) < 2:
                logger.warning(f"Not enough price data for {symbol} to perform arbitrage")
                return "hold"

            # Находим минимальную и максимальную цену
            min_price = min(prices.values())
            max_price = max(prices.values())
            price_diff = (max_price - min_price) / min_price

            # Генерируем сигнал
            if price_diff > self.price_diff_threshold:
                signal = "buy"  # Покупаем на бирже с низкой ценой, продаём на бирже с высокой
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Price Diff: {price_diff})")
            return signal
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return "hold"
