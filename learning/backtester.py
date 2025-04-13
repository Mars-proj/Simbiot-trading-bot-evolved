import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from strategies.rsi_strategy import RSIStrategy
from strategies.bollinger_strategy import BollingerStrategy
from strategies.macd_strategy import MACDStrategy

logger = setup_logging('backtester')

class Backtester:
    def __init__(self, market_state: dict, market_data):
        self.volatility = market_state['volatility']
        self.market_data = market_data

    async def run_backtest(self, symbols: list, strategy: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> dict:
        """Run a backtest for the specified symbols and strategy."""
        try:
            results = {}
            for symbol in symbols:
                # Получаем данные для символа
                klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
                if not klines:
                    logger.warning(f"No data for {symbol} on {exchange_name}")
                    continue

                # Инициализируем стратегию
                if strategy == 'rsi':
                    strat = RSIStrategy({'volatility': self.volatility}, market_data=self.market_data)
                elif strategy == 'bollinger':
                    strat = BollingerStrategy({'volatility': self.volatility}, market_data=self.market_data)
                elif strategy == 'macd':
                    strat = MACDStrategy({'volatility': self.volatility}, market_data=self.market_data)
                else:
                    logger.error(f"Unsupported strategy: {strategy}")
                    raise ValueError(f"Unsupported strategy: {strategy}")

                # Симулируем торговлю
                profit = 0
                for i in range(1, len(klines)):
                    signal = await strat.generate_signal(symbol, timeframe, i, exchange_name)
                    if signal == 'buy':
                        profit -= klines[i]['close']  # Покупаем
                    elif signal == 'sell' and profit < 0:
                        profit += klines[i]['close']  # Продаём

                results[symbol] = {'profit': profit}
                logger.info(f"Backtest result for {symbol}: {results[symbol]}")

            return results
        except Exception as e:
            logger.error(f"Failed to run backtest: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import asyncio
    from data_sources.market_data import MarketData
    from symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    backtester = Backtester(market_state, market_data=market_data)
    
    async def main():
        symbol_filter = SymbolFilter(market_state, market_data=market_data)
        symbols = await market_data.get_symbols('mexc')
        symbols = await symbol_filter.filter_symbols(symbols, 'mexc')
        result = await backtester.run_backtest(symbols[:1], 'rsi', '1h', 30, 'mexc')
        print(f"Backtest result: {result}")

    asyncio.run(main())
