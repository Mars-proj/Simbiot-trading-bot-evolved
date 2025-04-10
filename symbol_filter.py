from typing import List
import ccxt
from exchange_factory import ExchangeFactory
import pandas as pd
import logging

def setup_logging():
    logging.basicConfig(
        filename='symbol_filter.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def filter_symbols(exchange_id: str, symbols: List[str], min_volume: float, min_liquidity: float, max_volatility: float) -> List[str]:
    """Filter symbols based on volume, liquidity, and volatility."""
    setup_logging()
    try:
        exchange = ExchangeFactory.create_exchange(exchange_id)
        filtered_symbols = []

        for symbol in symbols:
            try:
                # Fetch ticker data
                ticker = exchange.fetch_ticker(symbol)
                volume = ticker['baseVolume'] if 'baseVolume' in ticker else 0.0

                # Fetch order book for liquidity
                order_book = exchange.fetch_order_book(symbol, limit=10)
                bid_ask_spread = (order_book['asks'][0][0] - order_book['bids'][0][0]) / order_book['bids'][0][0] if order_book['bids'] and order_book['asks'] else float('inf')

                # Fetch historical data for volatility
                ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=100)
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                volatility = df['close'].pct_change().std()

                # Apply filters
                if (volume >= min_volume and 
                    bid_ask_spread <= min_liquidity and 
                    volatility <= max_volatility):
                    filtered_symbols.append(symbol)
                    logging.info(f"Symbol {symbol} passed filters: volume={volume}, spread={bid_ask_spread}, volatility={volatility}")
                else:
                    logging.info(f"Symbol {symbol} filtered out: volume={volume}, spread={bid_ask_spread}, volatility={volatility}")
            except Exception as e:
                logging.warning(f"Failed to fetch data for {symbol}: {str(e)}")
                continue

        return filtered_symbols
    except Exception as e:
        logging.error(f"Failed to filter symbols: {str(e)}")
        raise
