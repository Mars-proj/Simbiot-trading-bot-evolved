import ccxt
import pandas as pd
from logging_setup import setup_logging

logger = setup_logging('data_utils')

def load_historical_data(exchange: ccxt.Exchange, symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
    """Load historical data for a symbol from an exchange."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        logger.info(f"Loaded {len(ohlcv)} candles for {symbol} from {exchange.id}")

        # Convert to DataFrame
        data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data['price'] = data['close']  # Use closing price as the main price
        return data
    except Exception as e:
        logger.error(f"Failed to load data for {symbol} from {exchange.id}: {str(e)}")
        raise

def load_multiple_symbols(exchange: ccxt.Exchange, symbols: list, timeframe: str, limit: int = 1000) -> dict:
    """Load historical data for multiple symbols."""
    try:
        data_dict = {}
        for symbol in symbols:
            data = load_historical_data(exchange, symbol, timeframe, limit)
            data_dict[symbol] = data
        logger.info(f"Loaded data for {len(symbols)} symbols")
        return data_dict
    except Exception as e:
        logger.error(f"Failed to load data for multiple symbols: {str(e)}")
        raise

def load_order_book(exchange: ccxt.Exchange, symbol: str, limit: int = 10) -> dict:
    """Load order book data for a symbol."""
    try:
        order_book = exchange.fetch_order_book(symbol, limit=limit)
        logger.info(f"Loaded order book for {symbol} from {exchange.id}")
        return order_book
    except Exception as e:
        logger.error(f"Failed to load order book for {symbol} from {exchange.id}: {str(e)}")
        raise

def preprocess_data(data: pd.DataFrame) -> pd.DataFrame:
    """Preprocess data for analysis."""
    try:
        # Remove NaNs
        data = data.dropna()

        # Add basic transformations
        data['returns'] = data['price'].pct_change()
        data['log_returns'] = np.log(data['price'] / data['price'].shift(1))
        return data
    except Exception as e:
        logger.error(f"Failed to preprocess data: {str(e)}")
        raise
