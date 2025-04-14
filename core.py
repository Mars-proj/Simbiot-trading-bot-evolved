import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import pickle
import os.path
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
        self.market_data = market_data  # Сохраняем market_data как атрибут
        self.strategy_manager = StrategyManager(market_state, market_data=market_data)
        self.online_learning = OnlineLearning(market_state, market_data=market_data)
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data=market_data)
        self.symbol_filter = SymbolFilter(market_data, market_state)
        self.exchange = MEXCAPI(market_state)
        self.risk_params = {
            'max_position_size': 0.1,
            'stop_loss_factor': 0.02,
            'trailing_stop_factor': 0.01,
        }
        self.positions = {}
        self.positions_file = "/root/trading_bot/cache/positions.pkl"
        self.load_positions()

    def load_positions(self):
        """Load open positions from file."""
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'rb') as f:
                    self.positions = pickle.load(f)
                logger.info(f"Loaded {len(self.positions)} positions from cache")
            except Exception as e:
                logger.warning(f"Failed to load positions: {str(e)}")
                self.positions = {}

    def save_positions(self):
        """Save open positions to file."""
        try:
            with open(self.positions_file, 'wb') as f:
                pickle.dump(self.positions, f)
            logger.info(f"Saved {len(self.positions)} positions to cache")
        except Exception as e:
            logger.warning(f"Failed to save positions: {str(e)}")

    async def monitor_positions(self, symbol: str, exchange_name: str, timeframe: str):
        """Monitor open positions and apply stop-loss or trailing stop."""
        if symbol not in self.positions:
            return

        position = self.positions[symbol]
        entry_price = position['price']
        quantity = position['quantity']
        signal = position['signal']
        stop_loss_price = position['stop_loss_price']
        trailing_stop_price = position.get('trailing_stop_price', entry_price)

        klines = await self.market_data.get_klines(symbol, timeframe, 1, exchange_name)
        if not klines:
            logger.warning(f"No klines data for {symbol}, cannot monitor position")
            return

        current_price = klines[-1]['close']

        if signal == 'buy':
            new_trailing_stop = current_price * (1 - self.risk_params['trailing_stop_factor'])
            trailing_stop_price = max(trailing_stop_price, new_trailing_stop)
        else:
            new_trailing_stop = current_price * (1 + self.risk_params['trailing_stop_factor'])
            trailing_stop_price = min(trailing_stop_price, new_trailing_stop)

        position['trailing_stop_price'] = trailing_stop_price

        should_close = False
        if signal == 'buy':
            if current_price <= stop_loss_price or current_price <= trailing_stop_price:
                should_close = True
        else:
            if current_price >= stop_loss_price or current_price >= trailing_stop_price:
                should_close = True

        if should_close:
            close_signal = 'sell' if signal == 'buy' else 'buy'
            order_result = await self.exchange.place_order(symbol, close_signal, quantity)
            if order_result:
                logger.info(f"Closed position for {symbol} at {current_price}: {order_result}")
                del self.positions[symbol]
                self.save_positions()
            else:
                logger.error(f"Failed to close position for {symbol}")

    async def run_trading(self, symbol: str, strategies: list, balance: float, timeframe: str, limit: int, exchange_name: str) -> list:
        """Run trading for a single symbol and execute orders with risk management."""
        try:
            trades = []

            await self.monitor_positions(symbol, exchange_name, timeframe)

            if symbol in self.positions:
                logger.info(f"Position already open for {symbol}, skipping new trade")
                return trades

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
                        max_balance = balance * self.risk_params['max_position_size']
                        quantity = min(max_balance / current_price, balance / current_price)

                        if quantity <= 0:
                            logger.warning(f"Insufficient balance to trade {symbol}")
                            continue

                        stop_loss_price = current_price * (1 - self.risk_params['stop_loss_factor']) if signal == 'buy' else current_price * (1 + self.risk_params['stop_loss_factor'])

                        order_result = await self.exchange.place_order(symbol, signal, quantity)
                        if not order_result:
                            logger.error(f"Failed to execute {signal} order for {symbol}")
                            continue

                        position = {
                            'symbol': symbol,
                            'signal': signal,
                            'price': current_price,
                            'quantity': quantity,
                            'stop_loss_price': stop_loss_price,
                            'trailing_stop_price': current_price
                        }
                        self.positions[symbol] = position
                        self.save_positions()

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
