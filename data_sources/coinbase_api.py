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

logger = setup_logging('coinbase_api')

class CoinbaseAPI:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.api_key = os.getenv('COINBASE_API_KEY')
        self.api_secret = os.getenv('COINBASE_API_SECRET')
        self.base_url = "https://api.coinbase.com"

        # Проверяем, что ключи загружены
        if not self.api_key or not self.api_secret:
            logger.error("Coinbase API keys not found in .env file")
            raise ValueError("Coinbase API keys not found in .env file")

    def _generate_signature(self, method: str, path: str, body: str, timestamp: str) -> str:
        """Generate signature for Coinbase API requests."""
        message = timestamp + method + path + body
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch klines data from Coinbase asynchronously."""
        try:
            # Преобразуем timeframe в формат Coinbase
            interval_map = {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '30m': 1800,
                '1h': 3600,
                '4h': 14400,
                '1d': 86400
            }
            granularity = interval_map.get(timeframe, 3600)

            # Параметры запроса
            symbol = symbol.replace('/', '-').upper()  # Coinbase использует формат, например, BTC-USD
            params = {
                'granularity': granularity
            }

            # Асинхронный запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/prices/{symbol}/candles", params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            # Преобразуем данные в формат, ожидаемый системой
            klines = [
                {
                    'timestamp': int(candle[0]),
                    'open': float(candle[3]),
                    'high': float(candle[1]),
                    'low': float(candle[2]),
                    'close': float(candle[4]),
                    'volume': float(candle[5])
                }
                for candle in data[-limit:]
            ]

            logger.info(f"Fetched {len(klines)} klines for {symbol} from Coinbase")
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from Coinbase: {str(e)}")
            raise

    async def get_symbols(self) -> list:
        """Fetch available trading symbols from Coinbase asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v2/currencies") as response:
                    response.raise_for_status()
                    data = await response.json()

            # Coinbase API не предоставляет прямой список пар, но мы можем получить валюты
            # Для простоты предположим, что пары формируются с USD
            symbols = [f"{currency['id']}/USD" for currency in data['data'] if currency['details']['type'] == 'crypto']
            logger.info(f"Fetched {len(symbols)} symbols from Coinbase")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Coinbase: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    coinbase_api = CoinbaseAPI(market_state)
    
    async def main():
        symbols = await coinbase_api.get_symbols()
        print(f"Available symbols: {symbols[:5]}")  # Первые 5 символов
        
        klines = await coinbase_api.get_klines("BTC/USD", "1h", 5)
        print(f"Klines for BTC/USD: {klines}")

    asyncio.run(main())
