import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import time
from core import TradingBotCore
from data_sources.market_data import MarketData
from utils.logging_setup import setup_logging

logger = setup_logging('start_trading_all')

class StartTradingAll:
    def __init__(self, market_state: dict):
        self.market_data = MarketData(market_state)
        self.core = TradingBotCore(market_state, market_data=self.market_data)
        self.interval = market_state.get('trading_interval', 60)  # Уменьшаем интервал с 300 до 60 секунд

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

async def main():
    market_state = {
        'volatility': 0.3,
        'min_liquidity': 500,
        'max_volatility': 1.0,
        'liquidity_period': 240,
        'trading_interval': 60  # Уменьшаем интервал с 300 до 60 секунд
    }
    starter = StartTradingAll(market_state)
    strategies = ['bollinger', 'rsi', 'macd']
    balance = 10000
    timeframe = '1h'
    limit = 200

    while True:
        try:
            trades = await starter.start_all(strategies, balance, timeframe, limit)
            print(f"Trading results: {trades}")
            logger.info(f"Waiting {starter.interval} seconds before the next iteration...")
            await asyncio.sleep(starter.interval)
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            logger.info(f"Retrying in {starter.interval} seconds...")
            await asyncio.sleep(starter.interval)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()
