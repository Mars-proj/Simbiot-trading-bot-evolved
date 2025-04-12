import asyncio
from trading_bot.logging_setup import setup_logging
from trading_bot.core import TradingBotCore
from trading_bot.symbol_filter import SymbolFilter
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('start_trading_all')

class StartTradingAll:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.core = TradingBotCore(market_state)
        self.symbol_filter = SymbolFilter(market_state)
        self.market_data = MarketData(market_state)

    async def start_all(self, strategies: list, account_balance: float, exchange_name: str = 'mexc', timeframe: str = '1h', limit: int = 30):
        """Start trading for all symbols and strategies asynchronously."""
        try:
            # Получаем список символов с биржи
            all_symbols = await self.market_data.get_symbols(exchange_name)
            
            # Применяем фильтры для выбора символов
            self.symbol_filter.setup_default_filters(min_liquidity=1000000, max_volatility=0.5)
            symbols = self.symbol_filter.filter_symbols(all_symbols, exchange_name)
            
            # Получаем данные для каждого символа асинхронно
            klines = {}
            tasks = []
            for symbol in symbols:
                tasks.append(self.market_data.get_klines(symbol, timeframe, limit, exchange_name))
            
            klines_results = await asyncio.gather(*tasks, return_exceptions=True)
            for symbol, result in zip(symbols, klines_results):
                if isinstance(result, Exception):
                    logger.warning(f"Skipping {symbol} due to error: {str(result)}")
                    continue
                klines[symbol] = result

            # Запускаем торговлю для каждого символа
            results = {}
            for symbol in klines:
                symbol_results = {}
                for strategy in strategies:
                    # Динамическая корректировка баланса на основе волатильности
                    adjusted_balance = account_balance * (1 - self.volatility / 2)
                    
                    trades = self.core.run_trading(symbol, strategy, adjusted_balance, timeframe, limit, exchange_name)
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
    strategies = ['bollinger', 'rsi']
    
    # Запускаем асинхронный метод
    results = asyncio.run(starter.start_all(strategies, 10000, 'mexc', '1h', 30))
    print(f"Trading results: {results}")
