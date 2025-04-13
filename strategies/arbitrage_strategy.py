import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from .strategy import Strategy

logger = setup_logging('arbitrage_strategy')

class ArbitrageStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state)
        self.market_data = market_data
        self.exchanges = ['mexc', 'binance']  # Биржи для арбитража

    async def find_arbitrage_opportunity(self, symbol: str) -> dict:
        """Find arbitrage opportunities between exchanges."""
        try:
            # Получаем цены с разных бирж асинхронно
            tasks = [self.market_data.get_klines(symbol, '1m', 1, exchange) for exchange in self.exchanges]
            klines = await asyncio.gather(*tasks, return_exceptions=True)

            prices = {}
            for exchange, kline in zip(self.exchanges, klines):
                if isinstance(kline, Exception):
                    logger.warning(f"Failed to fetch price for {symbol} on {exchange}: {str(kline)}")
                    continue
                if kline:
                    prices[exchange] = kline[-1]['close']
                else:
                    logger.warning(f"No price data for {symbol} on {exchange}")
                    continue

            if len(prices) < 2:
                return {'opportunity': None}

            # Находим разницу в ценах
            max_price_exchange = max(prices, key=prices.get)
            min_price_exchange = min(prices, key=prices.get)
            price_diff = prices[max_price_exchange] - prices[min_price_exchange]
            price_diff_percentage = (price_diff / prices[min_price_exchange]) * 100

            # Порог для арбитража (учитываем комиссию 0.1% на каждой бирже)
            arbitrage_threshold = 0.2  # 0.2% после учёта комиссий
            if price_diff_percentage > arbitrage_threshold:
                return {
                    'opportunity': {
                        'buy_exchange': min_price_exchange,
                        'sell_exchange': max_price_exchange,
                        'buy_price': prices[min_price_exchange],
                        'sell_price': prices[max_price_exchange],
                        'profit_percentage': price_diff_percentage
                    }
                }
            return {'opportunity': None}
        except Exception as e:
            logger.error(f"Failed to find arbitrage opportunity for {symbol}: {str(e)}")
            raise

    async def generate_signal(self, symbol: str, timeframe: str = '1m', limit: int = 1, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal based on arbitrage opportunities."""
        try:
            opportunity = await self.find_arbitrage_opportunity(symbol)
            if opportunity['opportunity']:
                logger.info(f"Arbitrage opportunity for {symbol}: Buy on {opportunity['opportunity']['buy_exchange']} at {opportunity['opportunity']['buy_price']}, Sell on {opportunity['opportunity']['sell_exchange']} at {opportunity['opportunity']['sell_price']}")
                return "buy"  # Сигнал для покупки на бирже с низкой ценой
            return "hold"
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from data_sources.market_data import MarketData
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    strategy = ArbitrageStrategy(market_state, market_data=market_data)
    symbol_filter = SymbolFilter(market_state, market_data=market_data)
    
    # Получаем символы
    symbols = asyncio.run(strategy.market_data.get_symbols('mexc'))
    symbols = symbol_filter.filter_symbols(symbols, 'mexc')
    
    if symbols:
        signal = asyncio.run(strategy.generate_signal(symbols[0], '1m', 1, 'mexc'))
        print(f"Signal for {symbols[0]}: {signal}")
    else:
        print("No symbols available for testing")
