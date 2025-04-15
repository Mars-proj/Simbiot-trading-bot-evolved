import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import asyncio
from utils.logging_setup import setup_logging
from utils.telegram_notifier import TelegramNotifier
from symbol_filter import SymbolFilter
from volatility_analyzer import VolatilityAnalyzer
from learning.online_learning import OnlineLearning
from strategies import StrategyManager
from data_sources.mexc_api import MEXCAPI
from data_sources.market_data import AsyncMarketData
from risk_management import RiskManager, PositionManager
from trading import OrderManager, RiskCalculator, TradeExecutor
from news_analyzer import NewsAnalyzer
from rl_decision_maker import RLDecisionMaker

logger = setup_logging('core')

class TradingBotCore:
    def __init__(self):
        logger.info("Starting initialization of TradingBotCore")
        self.exchanges = ["mexc", "binance"]
        self.timeframe = "1h"
        self.limit = 200
        self.iteration_interval = 60
        logger.info("Basic attributes initialized")

        self.mexc_api = MEXCAPI()
        logger.info("MEXCAPI initialized")

        self.market_data = AsyncMarketData()
        logger.info("AsyncMarketData initialized")

        self.news_analyzer = NewsAnalyzer()
        logger.info("NewsAnalyzer initialized")

        self.telegram_notifier = TelegramNotifier(
            bot_token="your_bot_token",
            chat_id="your_chat_id"
        )
        logger.info("TelegramNotifier initialized")

        self.market_state = {}
        logger.info("Market state initialized")

        self.symbol_filter = SymbolFilter(self.market_data, self.market_state)
        logger.info("SymbolFilter initialized")

        self.volatility_analyzer = VolatilityAnalyzer(self.market_state, self.market_data)
        logger.info("VolatilityAnalyzer initialized")

        self.online_learning = OnlineLearning(self.market_state, self.market_data)
        logger.info("OnlineLearning initialized")

        self.strategy_manager = StrategyManager(self.market_state, self.market_data, self.volatility_analyzer, self.online_learning)
        logger.info("StrategyManager initialized")

        self.rl_decision_maker = RLDecisionMaker([], self.strategy_manager.strategies)
        logger.info("RLDecisionMaker initialized")

        self.risk_manager = RiskManager(self.volatility_analyzer)
        logger.info("RiskManager initialized")

        self.position_manager = PositionManager()
        logger.info("PositionManager initialized")

        self.order_manager = OrderManager()
        logger.info("OrderManager initialized")

        self.risk_calculator = RiskCalculator(self.volatility_analyzer)
        logger.info("RiskCalculator initialized")

        self.trade_executors = {}
        for exchange in self.exchanges:
            self.trade_executors[exchange] = TradeExecutor(exchange)
            logger.info(f"TradeExecutor for {exchange} initialized")
        logger.info("Finished initialization of TradingBotCore")

    def get_symbols(self, exchange_name):
        return self.mexc_api.fetch_symbols() if exchange_name == "mexc" else self.market_data.exchanges[exchange_name].load_markets()

    def batch_symbols(self, symbols, batch_size=50):
        for i in range(0, len(symbols), batch_size):
            yield symbols[i:i + batch_size]

    async def start_trading(self, fetch_klines, train_model):
        """Start the trading process."""
        while True:
            try:
                for exchange_name in self.exchanges:
                    articles = self.news_analyzer.fetch_news()
                    critical_news = self.news_analyzer.analyze_news(articles)
                    if self.news_analyzer.should_pause_trading(critical_news):
                        message = "Pausing trading due to critical news: " + ", ".join([news['title'] for news in critical_news])
                        logger.warning(message)
                        self.telegram_notifier.send_message(message)
                        await asyncio.sleep(3600)
                        continue

                    logger.info(f"Starting trading iteration on {exchange_name}")
                    symbols = self.get_symbols(exchange_name)
                    logger.info(f"Fetched {len(symbols)} symbols from {exchange_name}")

                    for symbol_batch in self.batch_symbols(symbols):
                        tasks = []
                        for symbol in symbol_batch:
                            tasks.append(self.market_data.fetch_klines_with_semaphore(symbol, self.timeframe, self.limit, exchange_name))
                        klines_results = await asyncio.gather(*tasks)

                        for symbol, klines in zip(symbol_batch, klines_results):
                            if not klines:
                                logger.warning(f"No klines for {symbol} on {exchange_name}, skipping")
                                continue

                            train_success = await train_model(symbol, self.timeframe, self.limit, exchange_name)
                            if not train_success:
                                logger.warning(f"Failed to retrain model for {symbol} on {exchange_name}, skipping")
                                continue

                            self.rl_decision_maker.env.klines = klines
                            self.rl_decision_maker.train(total_timesteps=1000)

                            prediction = await self.online_learning.predict(symbol, self.timeframe, self.limit, exchange_name)
                            if prediction is not None:
                                signals = await self.strategy_manager.generate_signals(symbol, klines, prediction)
                                if signals:
                                    best_strategy = self.rl_decision_maker.select_strategy()
                                    signal = await best_strategy.generate_signal(symbol, klines, "1m", 200, exchange_name)
                                    if signal:
                                        signal['exchange_name'] = exchange_name
                                        await self.execute_trade(signal)
                            else:
                                logger.warning(f"No prediction for {symbol} on {exchange_name}, skipping trade execution")

                    logger.info(f"Trading iteration completed for {exchange_name}")
            except Exception as e:
                logger.error(f"Error in trading iteration: {str(e)}")
                message = f"Error in trading iteration: {str(e)}"
                self.telegram_notifier.send_message(message)
            finally:
                logger.info(f"Waiting {self.iteration_interval} seconds before the next iteration...")
                await asyncio.sleep(self.iteration_interval)

    async def execute_trade(self, signal):
        """Execute a trade asynchronously."""
        exchange_name = signal['exchange_name']
        risk = self.risk_calculator.calculate_risk(signal)
        if self.risk_manager.validate_risk(risk):
            position = await self.trade_executors[exchange_name].execute(signal)
            self.position_manager.add_position(signal['symbol'], position)
            logger.info(f"Executed trade for {signal['symbol']} on {exchange_name}: {signal}")
            message = f"Trade executed for {signal['symbol']} on {exchange_name}: {signal['signal']} at {signal['entry_price']}"
            self.telegram_notifier.send_message(message)
        else:
            logger.warning(f"Trade for {signal['symbol']} on {exchange_name} rejected due to high risk: {risk}")
            message = f"Trade for {signal['symbol']} on {exchange_name} rejected due to high risk: {risk}"
            self.telegram_notifier.send_message(message)

    async def close(self):
        """Close all resources asynchronously."""
        try:
            await self.market_data.close()
            for exchange_name, executor in self.trade_executors.items():
                await executor.close()
                logger.info(f"Closed TradeExecutor for {exchange_name}")
            logger.info("Closed all resources in TradingBotCore")
            self.telegram_notifier.send_message("TradingBotCore resources closed successfully")
        except Exception as e:
            logger.error(f"Failed to close TradingBotCore resources: {str(e)}")
            self.telegram_notifier.send_message(f"Failed to close TradingBotCore resources: {str(e)}")
