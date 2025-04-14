import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import asyncio
from utils.logging_setup import setup_logging
from symbol_filter import SymbolFilter
from volatility_analyzer import VolatilityAnalyzer
from learning.online_learning import OnlineLearning
from strategies import StrategyManager
from data_sources.mexc_api import MEXCAPI
from data_sources.market_data import AsyncMarketData
from risk_management import RiskManager, PositionManager
from trading import OrderManager, RiskCalculator, TradeExecutor

logger = setup_logging('core')

class TradingBotCore:
    def __init__(self):
        self.exchange_name = "mexc"
        self.timeframe = "1h"
        self.limit = 200
        self.iteration_interval = 60
        self.mexc_api = MEXCAPI()
        self.market_data = AsyncMarketData()
        self.market_state = {}  # Пустой словарь для состояния рынка
        self.symbol_filter = SymbolFilter(self.market_data, self.market_state)
        self.volatility_analyzer = VolatilityAnalyzer(self.market_state, self.market_data)
        self.online_learning = OnlineLearning(self.market_state, self.market_data)
        self.strategy_manager = StrategyManager(self.market_state, self.market_data, self.volatility_analyzer, self.online_learning)
        self.risk_manager = RiskManager(self.volatility_analyzer)
        self.position_manager = PositionManager()
        self.order_manager = OrderManager()
        self.risk_calculator = RiskCalculator(self.volatility_analyzer)
        self.trade_executor = TradeExecutor(self.exchange_name)

    def get_symbols(self):
        return self.mexc_api.fetch_symbols()

    def batch_symbols(self, symbols, batch_size=50):
        for i in range(0, len(symbols), batch_size):
            yield symbols[i:i + batch_size]

    async def start_trading(self, fetch_klines, train_model):
        """Start the trading process."""
        while True:
            try:
                logger.info(f"Starting trading iteration on {self.exchange_name}")
                symbols = self.get_symbols()
                logger.info(f"Fetched {len(symbols)} symbols from {self.exchange_name}")

                for symbol_batch in self.batch_symbols(symbols):
                    tasks = []
                    for symbol in symbol_batch:
                        tasks.append(fetch_klines(self.exchange_name, symbol, self.timeframe, self.limit))
                    klines_results = await asyncio.gather(*tasks)

                    for symbol, klines in zip(symbol_batch, klines_results):
                        if not klines:
                            logger.warning(f"No klines for {symbol}, skipping")
                            continue

                        train_success = await train_model(symbol, self.timeframe, self.limit, self.exchange_name)
                        if not train_success:
                            logger.warning(f"Failed to retrain model for {symbol}, skipping")
                            continue

                        prediction = await self.online_learning.predict(symbol, self.timeframe, self.limit, self.exchange_name)
                        if prediction is not None:
                            signals = self.strategy_manager.generate_signals(symbol, klines, prediction)
                            if signals:
                                for signal in signals:
                                    await self.execute_trade(signal)
                        else:
                            logger.warning(f"No prediction for {symbol}, skipping trade execution")

                logger.info("Trading iteration completed")
            except Exception as e:
                logger.error(f"Error in trading iteration: {str(e)}")
            finally:
                logger.info(f"Waiting {self.iteration_interval} seconds before the next iteration...")
                await asyncio.sleep(self.iteration_interval)

    async def execute_trade(self, signal):
        """Execute a trade asynchronously."""
        risk = self.risk_calculator.calculate_risk(signal)
        if self.risk_manager.validate_risk(risk):
            position = await self.trade_executor.execute(signal)
            self.position_manager.add_position(signal['symbol'], position)
            logger.info(f"Executed trade for {signal['symbol']}: {signal}")
        else:
            logger.warning(f"Trade for {signal['symbol']} rejected due to high risk: {risk}")

    async def close(self):
        """Close all resources asynchronously."""
        try:
            await self.market_data.close()
            await self.trade_executor.close()
            logger.info("Closed all resources in TradingBotCore")
        except Exception as e:
            logger.error(f"Failed to close TradingBotCore resources: {str(e)}")
