import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging

logger = setup_logging('symbol_filter')

class SymbolFilter:
    def __init__(self, market_data):
        self.market_data = market_data
        self.filters = {
            'min_liquidity': 1000000,
            'max_volatility': 0.5
        }
        logger.info(f"Set up default filters: {self.filters}")

    async def filter_symbols(self, symbols: list, exchange_name: str, timeframe: str) -> list:
        """Filter symbols based on liquidity and volatility using the specified timeframe."""
        filtered_symbols = []

        # Получаем список поддерживаемых таймфреймов для биржи
        supported_timeframes = await self.market_data.get_supported_timeframes(exchange_name, symbols[0] if symbols else '')
        if not supported_timeframes:
            logger.error(f"No supported timeframes found for {exchange_name}")
            return []

        # Если переданный timeframe не поддерживается, выбираем первый доступный
        if timeframe not in supported_timeframes:
            logger.warning(f"Timeframe {timeframe} not supported on {exchange_name}. Using {supported_timeframes[0]} instead.")
            timeframe = supported_timeframes[0]

        for symbol in symbols:
            try:
                # Fetch klines for the symbol to calculate liquidity and volatility
                klines = await self.market_data.get_klines(symbol, timeframe, 1, exchange_name)
                if not klines:
                    logger.warning(f"No klines data for {symbol} on {exchange_name} with timeframe {timeframe}, skipping")
                    continue

                # Calculate liquidity (using volume from the latest kline)
                latest_kline = klines[-1]
                liquidity = latest_kline['volume'] * latest_kline['close']
                if liquidity < self.filters['min_liquidity']:
                    logger.debug(f"Skipping {symbol} due to low liquidity: {liquidity}")
                    continue

                # Calculate volatility
                prices = [kline['close'] for kline in klines]
                volatility = (max(prices) - min(prices)) / min(prices) if min(prices) != 0 else float('inf')
                if volatility > self.filters['max_volatility']:
                    logger.debug(f"Skipping {symbol} due to high volatility: {volatility}")
                    continue

                filtered_symbols.append(symbol)
            except Exception as e:
                logger.warning(f"Error filtering {symbol}: {str(e)}")
                continue

        logger.info(f"Retrieved {len(filtered_symbols)} cached symbols for {exchange_name} with timeframe {timeframe}")
        return filtered_symbols
