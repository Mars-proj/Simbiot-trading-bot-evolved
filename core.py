import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from strategies.strategy_manager import StrategyManager
from learning.online_learning import OnlineLearning
from volatility_analyzer import VolatilityAnalyzer
from symbol_filter import SymbolFilter
from data_sources.mexc_api import MEXCAPI

logger = setup_logging('core')

class TradingBotCore:
    def __init__(self, market_state: dict, market_data):
        self.market_state = market_state  # Сохраняем market_state
        self.strategy_manager = StrategyManager(market_state, market_data=market_data)
        self.online_learning = OnlineLearning(market_state, market_data=market_data)
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data=market_data)
        self.symbol_filter = SymbolFilter(market_data, market_state)  # Передаём market_state
        self.exchange = MEXCAPI(market_state)

    async def run_trading(self, symbol: str, strategies: list, balance: float, timeframe: str, limit: int, exchange_name: str) -> list:
        """Run trading for a single symbol and execute orders."""
        try:
            trades = []
            predictions = await self.online_learning.predict(symbol, timeframe, limit, exchange_name)
            if not predictions:
                logger.warning(f"No predictions for {symbol}, proceeding with default strategy")
                predictions = []

            volatility = await self.volatility_analyzer.analyze_volatility(symbol, timeframe, limit, exchange_name)

            for strategy in strategies:
                try:
                    signal = await self.strategy_manager.generate_signal(symbol, strategy, timeframe, limit, exchange_name, predictions=predictions, volatility=volatility)
                    if signal in ['buy', 'sell']:
                        klines = await self.market_data.get_klines(symbol, timeframe, 1, exchange_name)
                        if not klines:
                            logger.warning(f"No klines data for {symbol}, skipping trade")
                            continue

                        current_price = klines[-1]['close']
                        quantity = balance / current_price

                        order_result = await self.exchange.place_order(symbol, signal, quantity)
                        if not order_result:
                            logger.error(f"Failed to execute {signal} order for {symbol}")
                            continue

                        trade = {
                            'symbol': symbol,
                            'strategy': strategy,
                            'signal': signal,
                            'balance': balance,
                            'quantity': quantity,
                            'price': current_price,
                            'order_result': order_result
                        }
                        trades.append(trade)
                        logger.info(f"Executed {signal} trade for {symbol}: {trade}")
                except Exception as e:
                    logger.warning(f"Error generating signal or executing trade for {symbol} with {strategy}: {str(e)}")
                    continue

            await self.online_learning.retrain(symbol, timeframe, limit, exchange_name)

            logger.info(f"Trading completed: {trades}")
            return trades
        except Exception as e:
            logger.error(f"Error in trading for {symbol}: {str(e)}")
            return []

    async def filter_symbols(self, symbols: list, exchange_name: str, timeframe: str) -> list:
        """Filter symbols using SymbolFilter."""
        return await self.symbol_filter.filter_symbols(symbols, exchange_name, timeframe)
