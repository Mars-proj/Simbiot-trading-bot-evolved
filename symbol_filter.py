import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('symbol_filter')

class SymbolFilter:
    def __init__(self, market_data, market_state: dict):
        self.market_data = market_data
        self.market_state = market_state
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data)
        self.filters = {
            'min_liquidity': self.market_state.get('min_liquidity', 500),
            'max_volatility': self.market_state.get('max_volatility', 1.0),
            'liquidity_period': self.market_state.get('liquidity_period', 240)
        }
        logger.info(f"Set up filters: {self.filters}")

    async def determine_liquidity_period(self, symbols: list, exchange_name: str, timeframe: str) -> int:
        """Determine the optimal liquidity period based on market volatility."""
        try:
            sample_symbols = symbols[:5] if len(symbols) >= 5 else symbols
            volatilities = []

            for symbol in sample_symbols:
                volatility = await self.volatility_analyzer.analyze_volatility(symbol, timeframe, 60, exchange_name)
                volatilities.append(volatility)

            avg_volatility = sum(volatilities) / len(volatilities) if volatilities else 0.0
            logger.info(f"Average market volatility: {avg_volatility}")

            if avg_volatility > 0.5:
                period = 60  # 1 час
            elif avg_volatility >= 0.2:
                period = 240  # 4 часа
            else:
                period = 500  # Ограничиваем максимум до 500 свечей (MEXC API limit)

            logger.info(f"Selected liquidity period of {period} candles based on market volatility: {avg_volatility}")
            return period
        except Exception as e:
            logger.error(f"Failed to determine liquidity period, using default (240): {str(e)}")
            return 240

    async def filter_symbols(self, symbols: list, exchange_name: str, timeframe: str) -> list:
        """Filter symbols based on liquidity and volatility using the specified timeframe."""
        filtered_symbols = []
        supported_timeframes = await self.market_data.get_supported_timeframes(exchange_name, symbols[0] if symbols else '')
        if not supported_timeframes:
            logger.error(f"No supported timeframes found for {exchange_name}")
            return []

        if timeframe not in supported_timeframes:
            logger.warning(f"Timeframe {timeframe} not supported on {exchange_name}. Using {supported_timeframes[0]} instead.")
            timeframe = supported_timeframes[0]

        self.filters['liquidity_period'] = await self.determine_liquidity_period(symbols, exchange_name, timeframe)

        for symbol in symbols:
            try:
                klines = await self.market_data.get_klines(symbol, timeframe, self.filters['liquidity_period'], exchange_name)
                if not klines:
                    logger.warning(f"No klines data for {symbol} on {exchange_name} with timeframe {timeframe}, skipping")
                    continue

                total_volume = sum(kline['volume'] for kline in klines)
                latest_price = klines[-1]['close']
                liquidity = total_volume * latest_price / self.filters['liquidity_period']
                if liquidity < self.filters['min_liquidity']:
                    logger.debug(f"Skipping {symbol} due to low liquidity: {liquidity}")
                    continue

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
