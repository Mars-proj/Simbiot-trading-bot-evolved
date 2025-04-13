import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

import asyncio
from utils.logging_setup import setup_logging
from core import TradingBotCore
from symbol_filter import SymbolFilter
from data_sources.market_data import MarketData

logger = setup_logging('start_trading_all')

class StartTradingAll:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)
        self.core = TradingBotCore(market_state, market_data=self.market_data)
        self.symbol_filter = SymbolFilter(market_state, market_data=self.market_data)

    async def start_all(self, strategies: list, account_balance: float, preferred_exchange: str = 'mexc', timeframe: str = '1h', limit: int = 30):
        """Start trading for all symbols and strategies asynchronously, using available exchanges."""
        try:
            # Получаем список доступных бирж
            available_exchanges = self.market_data.get_available_exchanges()
            if not available_exchanges:
                logger.error("No exchanges available for trading")
                return {}

            # Выбираем биржу: предпочитаем MEXC, если доступна, иначе первую доступную
            exchange_name = preferred_exchange if preferred_exchange in available_exchanges else available_exchanges[0]
            logger.info(f"Using exchange: {exchange_name}")

            # Получаем список символов с биржи
            all_symbols = await self.market_data.get_symbols(exchange_name)
            if not all_symbols:
                logger.warning(f"No symbols available on {exchange_name}")
                return {}

            # Применяем фильтры для выбора символов
            self.symbol_filter.setup_default_filters(min_liquidity=1000000, max_volatility=0.5)
            symbols = await self.symbol_filter.filter_symbols(all_symbols, exchange_name)
            if not symbols:
                logger.warning(f"No symbols passed the filter on {exchange_name}")
                return {}

            # Получаем данные для каждого символа асинхронно
            klines = {}
            tasks = []
            for symbol in symbols:
                tasks.append(self.market_data.get_klines(symbol, timeframe, limit, exchange_name))
            
            klines_results = await asyncio.gather(*tasks, return_exceptions=True)
            for symbol, result in zip(symbols, klines_results):
                if isinstance(result, Exception) or not result:
                    logger.warning(f"Skipping {symbol} due to error: {str(result) if isinstance(result, Exception) else 'No data'}")
                    continue
                klines[symbol] = result

            # Запускаем торговлю для каждого символа
            results = {}
            for symbol in klines:
                symbol_results = {}
                for strategy in strategies:
                    # Динамическая корректировка баланса на основе волатильности
                    adjusted_balance = account_balance * (1 - self.volatility / 2)
                    
                    trades = await self.core.run_trading(symbol, strategy, adjusted_balance, timeframe, limit, exchange_name)
                    symbol_results[strategy] = trades
                results[symbol] = symbol_results
            
            logger.info(f"Trading started for all symbols: {results}")
            return results
        except Exception as e:
            logger.error(f"Failed to start trading for all: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    starter = StartTradingAll(market_state)
    strategies = ['bollinger', 'rsi', 'arbitrage']
    
    # Запускаем асинхронный метод
    results = asyncio.run(starter.start_all(strategies, 10000, 'mexc', '1h', 30))
    print(f"Trading results: {results}")
