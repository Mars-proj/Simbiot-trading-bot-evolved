import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from core import TradingBotCore
from utils.logging_setup import setup_logging, close_loggers
from data_sources.market_data import AsyncMarketData
from learning.online_learning import OnlineLearning

logger = setup_logging('start_trading_all')
market_data_instance = AsyncMarketData()

async def fetch_klines(exchange_name, symbol, timeframe, limit):
    """Fetch klines asynchronously."""
    try:
        klines = await market_data_instance.get_klines(symbol, timeframe, limit, exchange_name)
        logger.info(f"Fetched klines for {symbol} on {exchange_name}, result: {type(klines)}")
        return klines
    except Exception as e:
        logger.error(f"Failed to fetch klines for {symbol} on {exchange_name}: {str(e)}")
        return None

async def train_model(symbol, timeframe, limit, exchange_name):
    """Train a model asynchronously."""
    market_state = {}
    try:
        online_learning = OnlineLearning(market_state, market_data_instance)
        await online_learning.retrain(symbol, timeframe, limit, exchange_name)
        logger.info(f"Model retrained for {symbol} on {exchange_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to retrain model for {symbol} on {exchange_name}: {str(e)}")
        return False

async def main():
    bot = TradingBotCore()
    try:
        await bot.start_trading(fetch_klines, train_model)
    finally:
        await bot.close()
        await market_data_instance.close()
        close_loggers()

if __name__ == "__main__":
    asyncio.run(main())
