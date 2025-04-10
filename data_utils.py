import ccxt
import pandas as pd
from exchange_factory import ExchangeFactory
import logging

def setup_logging():
    logging.basicConfig(
        filename='data_utils.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def load_historical_data(exchange_id: str, symbol: str, timeframe: str, limit: int = 1000) -> pd.DataFrame:
    """Load historical data for a symbol from an exchange."""
    setup_logging()
    try:
        exchange = ExchangeFactory.create_exchange(exchange_id)
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        logging.info(f"Loaded {len(ohlcv)} candles for {symbol} from {exchange_id}")

        # Convert to DataFrame
        data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
        data['price'] = data['close']  # Use closing price as the main price
        return data
    except Exception as e:
        logging.error(f"Failed to load data for {symbol} from {exchange_id}: {str(e)}")
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
        logging.error(f"Failed to preprocess data: {str(e)}")
        raise
