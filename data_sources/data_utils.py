import ccxt
import pandas as pd
import redis
from logging_setup import setup_logging

logger = setup_logging('data_utils')

# Redis client for caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def load_historical_data(exchange: ccxt.Exchange, symbol: str, timeframe: str, market_state: dict, limit: int = None) -> pd.DataFrame:
    """Load historical data for a symbol from an exchange with dynamic limit and caching."""
    try:
        # Determine dynamic limit based on market state
        if limit is None:
            volatility = market_state['volatility']
            limit = int(500 * (1 + volatility))  # Higher volatility -> more data

        # Check cache
        cache_key = f"ohlcv:{symbol}:{timeframe}:{limit}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info(f"Loaded {symbol} OHLCV data from cache")
            return pd.read_pickle(cached_data)

        # Fetch data
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        logger.info(f"Loaded {len(ohlcv)} candles for {symbol} from {exchange.id}")

        # Convert to DataFrame
        data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data['price'] = data['close']  # Use closing price as the main price

        # Cache the data for 5 minutes
        redis_client.setex(cache_key, 300, data.to_pickle())
        return data
    except Exception as e:
        logger.error(f"Failed to load data for {symbol} from {exchange.id}: {str(e)}")
        raise

def load_multiple_symbols(exchange: ccxt.Exchange, symbols: list, timeframe: str, market_state: dict, limit: int = None) -> dict:
    """Load historical data for multiple symbols."""
    try:
        data_dict = {}
        for symbol in symbols:
            data = load_historical_data(exchange, symbol, timeframe, market_state, limit)
            data_dict[symbol] = data
        logger.info(f"Loaded data for {len(symbols)} symbols")
        return data_dict
    except Exception as e:
        logger.error(f"Failed to load data for multiple symbols: {str(e)}")
        raise

def load_order_book(exchange: ccxt.Exchange, symbol: str, market_state: dict, limit: int = None) -> dict:
    """Load order book data for a symbol with dynamic limit and caching."""
    try:
        # Determine dynamic limit based on market state
        if limit is None:
            volatility = market_state['volatility']
            limit = int(10 * (1 + volatility))  # Higher volatility -> more depth

        # Check cache
        cache_key = f"order_book:{symbol}:{limit}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info(f"Loaded {symbol} order book from cache")
            return pd.read_pickle(cached_data)

        # Fetch data
        order_book = exchange.fetch_order_book(symbol, limit=limit)
        logger.info(f"Loaded order book for {symbol} from {exchange.id}")

        # Cache the data for 1 minute
        redis_client.setex(cache_key, 60, pd.to_pickle(order_book))
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
