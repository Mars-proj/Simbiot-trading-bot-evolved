import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import time
from celery_app import fetch_klines_task, train_model_task
from core import TradingBotCore
from data_sources.market_data import MarketData
from utils.logging_setup import setup_logging

logger = setup_logging('start_trading_all')

async def main():
    exchange_name = 'mexc'
    timeframe = '1h'
    limit = 200
    interval = 60  # Interval between iterations in seconds

    market_data = MarketData()
    try:
        await market_data.initialize_exchange(exchange_name)
        core = TradingBotCore({}, market_data)

        while True:
            try:
                logger.info(f"Starting trading iteration on {exchange_name}")
                symbols = await core.get_symbols(exchange_name, timeframe, limit)

                # Parallel fetching of klines using Celery
                klines_tasks = []
                for symbol in symbols:
                    task = fetch_klines_task.delay(exchange_name, symbol, timeframe, limit)
                    klines_tasks.append((symbol, task))

                # Parallel retraining of models using Celery
                retrain_tasks = []
                for symbol in symbols:
                    task = train_model_task.delay(symbol, timeframe, limit, exchange_name)
                    retrain_tasks.append(task)

                # Process klines and execute trades
                trades = {}
                for symbol, task in klines_tasks:
                    klines = task.get(timeout=300)  # Wait up to 5 minutes for the task
                    if klines:
                        trades[symbol] = await core.process_symbol(symbol, timeframe, limit, exchange_name, klines)
                    else:
                        logger.warning(f"No klines data for {symbol}, skipping")

                # Wait for retraining to complete
                for task in retrain_tasks:
                    task.get(timeout=300)  # Wait up to 5 minutes for the task

                logger.info(f"Trading iteration completed: {trades}")
                logger.info(f"Waiting {interval} seconds before the next iteration...")
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in trading iteration: {str(e)}")
                time.sleep(interval)
    finally:
        await market_data.close()

if __name__ == "__main__":
    asyncio.run(main())
