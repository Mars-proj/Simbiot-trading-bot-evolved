import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from core import TradingBotCore
from utils.logging_setup import setup_logging
from data_sources.market_data import AsyncMarketData
from learning.online_learning import OnlineLearning

logger = setup_logging('start_trading_all')

async def fetch_klines(exchange_name, symbol, timeframe, limit):
    """Fetch klines asynchronously."""
    market_data_instance = AsyncMarketData()
    try:
        klines = await market_data_instance.get_klines(symbol, timeframe, limit, exchange_name)
        logger.info(f"Fetched klines for {symbol} on {exchange_name}, result: {type(klines)}")
        return klines
    except Exception as e:
        logger.error(f"Failed to fetch klines for {symbol} on {exchange_name}: {str(e)}")
        return None
    finally:
        await market_data_instance.close()

async def train_model(symbol, timeframe, limit, exchange_name):
    """Train a model asynchronously."""
    market_data_instance = AsyncMarketData()
    market_state = {}
    try:
        online_learning = OnlineLearning(market_state, market_data_instance)
        await online_learning.retrain(symbol, timeframe, limit, exchange_name)
        logger.info(f"Model retrained for {symbol} on {exchange_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to retrain model for {symbol} on {exchange_name}: {str(e)}")
        return False
    finally:
        await market_data_instance.close()

async def main():
    bot = TradingBotCore()
    try:
        await bot.start_trading(fetch_klines, train_model)
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
