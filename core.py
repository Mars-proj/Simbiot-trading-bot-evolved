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
        self.market_state = market_state
        self.strategy_manager = StrategyManager(market_state, market_data=market_data)
        self.online_learning = OnlineLearning(market_state, market_data=market_data)
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data=market_data)
        self.symbol_filter = SymbolFilter(market_data, market_state)
        self.exchange = MEXCAPI(market_state)
        self.risk_params = {
            'max_position_size': 0.1,  # Максимум 10% от баланса на одну позицию
            'stop_loss_factor': 0.02,  # Стоп-лосс на уровне 2% от цены входа
        }

    async def run_trading(self, symbol: str, strategies: list, balance: float, timeframe: str, limit: int, exchange_name: str) -> list:
        """Run trading for a single symbol and execute orders with risk management."""
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
                        # Ограничиваем размер позиции
                        max_balance = balance * self.risk_params['max_position_size']
                        quantity = min(max_balance / current_price, balance / current_price)

                        if quantity <= 0:
                            logger.warning(f"Insufficient balance to trade {symbol}")
                            continue

                        # Рассчитываем цену стоп-лосса
                        stop_loss_price = current_price * (1 - self.risk_params['stop_loss_factor']) if signal == 'buy' else current_price * (1 + self.risk_params['stop_loss_factor'])

                        # Используем лимитный ордер для входа
                        order_result = await self.exchange.place_order(symbol, signal, quantity)
                        if not order_result:
                            logger.error(f"Failed to execute {signal} order for {symbol}")
                            continue

                        # Здесь можно добавить логику для установки стоп-лосса через API MEXC (например, условный ордер),
                        # но MEXC API не поддерживает прямые стоп-лоссы в текущем формате.
                        # Мы будем отслеживать цену в будущих итерациях для реализации программного стоп-лосса.

                        trade = {
                            'symbol': symbol,
                            'strategy': strategy,
                            'signal': signal,
                            'balance': balance,
                            'quantity': quantity,
                            'price': current_price,
                            'stop_loss_price': stop_loss_price,
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
