from typing import List
from logging_setup import setup_logging

logger = setup_logging('symbol_filter')

def filter_symbols(exchange: object, symbols: List[str], min_volume: float = 1000.0, min_liquidity: float = 0.01, max_volatility: float = 0.05) -> List[str]:
    """Filter symbols based on market conditions."""
    try:
        filtered_symbols = []

        for symbol in symbols:
            try:
                # Fetch ticker data
                ticker = exchange.fetch_ticker(symbol)
                volume = ticker['baseVolume']
                bid_ask_spread = (ticker['ask'] - ticker['bid']) / ticker['bid'] if ticker['bid'] > 0 else float('inf')
                volatility = ticker['high'] / ticker['low'] - 1 if ticker['low'] > 0 else float('inf')

                # Apply filters
                if (volume >= min_volume and
                    bid_ask_spread <= min_liquidity and
                    volatility <= max_volatility):
                    filtered_symbols.append(symbol)
            except Exception as e:
                logger.warning(f"Failed to fetch data for {symbol}: {str(e)}")
                continue

        logger.info(f"Filtered {len(filtered_symbols)} out of {len(symbols)} symbols")
        return filtered_symbols
    except Exception as e:
        logger.error(f"Failed to filter symbols: {str(e)}")
        raise
