import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import aiohttp
from utils.logging_setup import setup_logging
from dotenv import load_dotenv
import os
import hmac
import hashlib
import time

# Загружаем переменные из .env
load_dotenv()

logger = setup_logging('bitstamp_api')

class BitstampAPI:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.api_key = os.getenv('BITSTAMP_API_KEY')
        self.api_secret = os.getenv('BITSTAMP_API_SECRET')
        self.base_url = "https://www.bitstamp.net/api/v2"

        # Проверяем, что ключи загружены
        if not self.api_key or not self.api_secret:
            logger.error("Bitstamp API keys not found in .env file")
            raise ValueError("Bitstamp API keys not found in .env file")

    def _generate_signature(self, nonce: str, timestamp: str) -> str:
        """Generate signature for Bitstamp API requests."""
        message = f"BITSTAMP {self.api_key}{timestamp}{nonce}GET/api/v2/ohlc/"
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch klines data from Bitstamp asynchronously."""
        try:
            # Преобразуем timeframe в формат Bitstamp
            interval_map = {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '30m': 1800,
                '1h': 3600,
                '4h': 14400,
                '1d': 86400
            }
            interval = interval_map.get(timeframe, 3600)

            # Параметры запроса
            params = {
                'pair': symbol.replace('/', '').lower(),  # Bitstamp использует формат, например, btcusd
                'step': interval,
                'limit': limit
            }

            # Асинхронный запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/ohlc/{params['pair']}", params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            if 'data' not in data or 'ohlc' not in data['data']:
                raise Exception("Invalid response from Bitstamp API")

            # Преобразуем данные в формат, ожидаемый системой
            klines = [
                {
                    'timestamp': int(kline['timestamp']),
                    'open': float(kline['open']),
                    'high': float(kline['high']),
                    'low': float(kline['low']),
                    'close': float(kline['close']),
                    'volume': float(kline['volume'])
                }
                for kline in data['data']['ohlc']
            ]

            logger.info(f"Fetched {len(klines)} klines for {symbol} from Bitstamp")
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from Bitstamp: {str(e)}")
            raise

    async def get_symbols(self) -> list:
        """Fetch available trading symbols from Bitstamp asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/trading-pairs-info/") as response:
                    response.raise_for_status()
                    data = await response.json()

            symbols = [pair['name'] for pair in data if pair['trading'] == 'Enabled']
            logger.info(f"Fetched {len(symbols)} symbols from Bitstamp")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Bitstamp: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    bitstamp_api = BitstampAPI(market_state)
    
    async def main():
        symbols = await bitstamp_api.get_symbols()
        print(f"Available symbols: {symbols[:5]}")  # Первые 5 символов
        
        klines = await bitstamp_api.get_klines("BTC/USD", "1h", 5)
        print(f"Klines for BTC/USD: {klines}")

    asyncio.run(main())
