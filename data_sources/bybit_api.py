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

logger = setup_logging('bybit_api')

class BybitAPI:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.api_secret = os.getenv('BYBIT_API_SECRET')
        self.base_url = "https://api.bybit.com"

        # Проверяем, что ключи загружены
        if not self.api_key or not self.api_secret:
            logger.error("Bybit API keys not found in .env file")
            raise ValueError("Bybit API keys not found in .env file")

    def _generate_signature(self, params: dict) -> str:
        """Generate signature for Bybit API requests."""
        query_string = '&'.join([f"{key}={params[key]}" for key in sorted(params.keys())])
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch klines data from Bybit asynchronously."""
        try:
            # Преобразуем timeframe в формат Bybit
            interval_map = {
                '1m': '1',
                '5m': '5',
                '15m': '15',
                '30m': '30',
                '1h': '60',
                '4h': '240',
                '1d': 'D'
            }
            interval = interval_map.get(timeframe, '60')

            # Параметры запроса
            params = {
                'symbol': symbol.replace('/', ''),  # Bybit использует формат, например, BTCUSDT
                'interval': interval,
                'limit': limit,
                'category': 'spot'
            }

            # Асинхронный запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v5/market/kline", params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            if data['retCode'] != 0:
                raise Exception(data['retMsg'])

            # Преобразуем данные в формат, ожидаемый системой
            klines = [
                {
                    'timestamp': int(kline[0] / 1000),  # Время в секундах
                    'open': float(kline[1]),
                    'high': float(kline[2]),
                    'low': float(kline[3]),
                    'close': float(kline[4]),
                    'volume': float(kline[5])
                }
                for kline in data['result']['list']
            ]

            logger.info(f"Fetched {len(klines)} klines for {symbol} from Bybit")
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from Bybit: {str(e)}")
            raise

    async def get_symbols(self) -> list:
        """Fetch available trading symbols from Bybit asynchronously."""
        try:
            params = {'category': 'spot'}
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v5/market/instruments-info", params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            if data['retCode'] != 0:
                raise Exception(data['retMsg'])

            symbols = [symbol['symbol'].replace('_', '/') for symbol in data['result']['list'] if symbol['status'] == 'Trading']
            logger.info(f"Fetched {len(symbols)} symbols from Bybit")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Bybit: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    bybit_api = BybitAPI(market_state)
    
    async def main():
        symbols = await bybit_api.get_symbols()
        print(f"Available symbols: {symbols[:5]}")  # Первые 5 символов
        
        klines = await bybit_api.get_klines("BTC/USDT", "1h", 5)
        print(f"Klines for BTC/USDT: {klines}")

    asyncio.run(main())
