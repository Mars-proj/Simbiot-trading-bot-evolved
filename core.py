import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import pickle
import os.path
import time
from utils.logging_setup import setup_logging
from strategies.strategy_manager import StrategyManager
from learning.online_learning import OnlineLearning
from risk_management.risk_manager import RiskManager
from risk_management.position_manager import PositionManager
from volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('core')

class TradingBotCore:
    def __init__(self, market_state, market_data):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = VolatilityAnalyzer()
        self.online_learning = OnlineLearning(self.market_state, self.market_data)
        self.strategy_manager = StrategyManager(self.market_state, self.market_data, self.volatility_analyzer, self.online_learning)
        self.risk_manager = RiskManager(self.volatility_analyzer)
        self.position_manager = PositionManager()

    async def get_symbols(self, exchange_name: str, timeframe: str, limit: int):
        """Get filtered symbols for trading."""
        try:
            all_symbols = await self.market_data.exchanges[exchange_name].fetch_tickers()
            symbols = list(all_symbols.keys())
            logger.info(f"Fetched {len(symbols)} symbols from {exchange_name}")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from {exchange_name}: {str(e)}")
            return []

    async def process_symbol(self, symbol: str, timeframe: str, limit: int, exchange_name: str, klines=None):
        """Process a single symbol and execute trades."""
        try:
            if klines is None:
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                return []

            # Calculate risk and position limits
            trade_size = self.risk_manager.calculate_risk(symbol, timeframe, limit, exchange_name)
            if not self.risk_manager.check_risk_limits(trade_size, symbol, timeframe, limit, exchange_name):
                logger.warning(f"Trade size {trade_size} for {symbol} exceeds risk limits")
                return []

            # Check position limits
            current_position = self.position_manager.get_position(symbol)
            if current_position + trade_size > self.position_manager.capital * self.position_manager.max_position_size:
                logger.warning(f"Position size for {symbol} exceeds maximum allowed")
                return []

            # Generate signals and execute trades
            signals = await self.strategy_manager.generate_signals(symbol, timeframe, limit, exchange_name, klines)
            trades = []
            for signal in signals:
                trade = await self.execute_trade(signal, trade_size)
                if trade:
                    trades.append(trade)
                    self.position_manager.add_position(symbol, trade_size)
            return trades
        except Exception as e:
            logger.error(f"Failed to process symbol {symbol}: {str(e)}")
            return []

    async def execute_trade(self, signal, trade_size):
        """Execute a trade based on a signal."""
        try:
            symbol = signal['symbol']
            strategy = signal['strategy']
            signal_type = signal['signal']
            entry_price = signal.get('entry_price', 0)

            # Calculate stop-loss based on volatility
            volatility = self.volatility_analyzer.get_volatility(symbol, signal['timeframe'], signal['limit'], signal['exchange_name'])
            stop_loss = self.risk_manager.calculate_stop_loss(entry_price, volatility)

            # Simulate trade execution
            trade = {
                'symbol': symbol,
                'strategy': strategy,
                'signal': signal_type,
                'entry_price': entry_price,
                'trade_size': trade_size,
                'stop_loss': stop_loss,
                'timestamp': time.time()
            }
            logger.info(f"Executed trade: {trade}")
            return trade
        except Exception as e:
            logger.error(f"Failed to execute trade: {str(e)}")
            return None
