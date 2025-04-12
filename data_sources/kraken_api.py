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
import base64
import time

# Загружаем переменные из .env
load_dotenv()

logger = setup_logging('kraken_api')

class KrakenAPI:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.api_key = os.getenv('KRAKEN_API_KEY')
        self.api_secret = os.getenv('KRAKEN_API_SECRET')
        self.base_url = "https://api.kraken.com"

        # Проверяем, что ключи загружены
        if not self.api_key or not self.api_secret:
            logger.error("Kraken API keys not found in .env file")
            raise ValueError("Kraken API keys not found in .env file")

    def _generate_signature(self, path: str, data: dict, nonce: int) -> str:
        """Generate signature for Kraken API requests."""
        postdata = '&'.join([f"{key}={data[key]}" for key in sorted(data.keys())])
        encoded = (str(nonce) + postdata).encode('utf-8')
        message = path.encode('utf-8') + hashlib.sha256(encoded).digest()
        signature = hmac.new(base64.b64decode(self.api_secret), message, hashlib.sha512)
        return base64.b64encode(signature.digest()).decode('utf-8')

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch klines data from Kraken asynchronously."""
        try:
            # Преобразуем timeframe в формат Kraken
            interval_map = {
                '1m': 1,
                '5m': 5,
                '15m': 15,
                '30m': 30,
                '1h': 60,
                '4h': 240,
                '1d': 1440
            }
            interval = interval_map.get(timeframe, 60)

            # Параметры запроса
            params = {
                'pair': symbol.replace('/', ''),  # Kraken использует формат, например, XBTUSD
                'interval': interval
            }

            # Асинхронный запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/0/public/OHLC", params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            if data['error']:
                raise Exception(data['error'])

            # Преобразуем данные в формат, ожидаемый системой
            klines = [
                {
                    'timestamp': int(kline[0]),  # Время в секундах
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[6])
                }
                for kline in list(data['result'].values())[0][-limit:]
            ]

            logger.info(f"Fetched {len(klines)} klines for {symbol} from Kraken")
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from Kraken: {str(e)}")
            raise

    async def get_symbols(self) -> list:
        """Fetch available trading symbols from Kraken asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/0/public/AssetPairs") as response:
                    response.raise_for_status()
                    data = await response.json()

            if data['error']:
                raise Exception(data['error'])

            symbols = [pair.replace('_', '/') for pair in data['result'].keys() if data['result'][pair]['status'] == 'online']
            logger.info(f"Fetched {len(symbols)} symbols from Kraken")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Kraken: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    kraken_api = KrakenAPI(market_state)
    
    async def main():
        symbols = await kraken_api.get_symbols()
        print(f"Available symbols: {symbols[:5]}")  # Первые 5 символов
        
        klines = await kraken_api.get_klines("XBT/USD", "1h", 5)
        print(f"Klines for XBT/USD: {klines}")

    asyncio.run(main())
