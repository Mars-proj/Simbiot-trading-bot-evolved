import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from core import TradingBotCore
from data_sources.market_data import MarketData
from utils.logging_setup import setup_logging

logger = setup_logging('start_trading_all')

class StartTradingAll:
    def __init__(self, market_state: dict):
        self.market_data = MarketData(market_state)
        self.core = TradingBotCore(market_state, market_data=self.market_data)

    async def start_all(self, strategies: list, balance: float, timeframe: str, limit: int):
        """Start trading for all symbols on the first available exchange, prioritizing MEXC."""
        try:
            available_exchanges = self.market_data.get_available_exchanges()
            if not available_exchanges:
                logger.error("No exchanges available for trading")
                return []

            exchange_name = 'mexc' if 'mexc' in available_exchanges else available_exchanges[0]
            logger.info(f"Using exchange: {exchange_name}")

            symbols = await self.market_data.get_symbols(exchange_name)
            if not symbols:
                logger.error(f"No symbols found for exchange: {exchange_name}")
                return []

            filtered_symbols = await self.core.filter_symbols(symbols, exchange_name, timeframe)
            if not filtered_symbols:
                logger.error(f"No symbols passed filtering for exchange: {exchange_name}")
                return []

            trades = []
            for symbol in filtered_symbols:
                try:
                    trade = await self.core.run_trading(symbol, strategies, balance / len(filtered_symbols), timeframe, limit, exchange_name)
                    trades.extend(trade)
                except Exception as e:
                    logger.warning(f"Skipping {symbol} due to error: {str(e)}")
                    continue

            logger.info(f"Trading iteration completed: {trades}")
            return trades
        except Exception as e:
            logger.error(f"Failed to start trading for all: {str(e)}")
            raise

if __name__ == "__main__":
    market_state = {
        'volatility': 0.3,
        'min_liquidity': 500,  # Ещё снижаем порог для теста
        'max_volatility': 1.0,  # Увеличиваем допустимую волатильность
        'liquidity_period': 240  # 4 часа
    }
    starter = StartTradingAll(market_state)
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(starter.start_all(['bollinger', 'rsi', 'macd'], 10000, '1h', 30))
    print(f"Trading results: {results}")
    loop.close()
