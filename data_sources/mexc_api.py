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

logger = setup_logging('mexc_api')

class MEXCAPI:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.api_key = os.getenv('MEXC_API_KEY')
        self.api_secret = os.getenv('MEXC_API_SECRET')
        self.base_url = "https://api.mexc.com"

        # Проверяем, что ключи загружены
        if not self.api_key or not self.api_secret:
            logger.error("MEXC API keys not found in .env file")
            raise ValueError("MEXC API keys not found in .env file")

    def _generate_signature(self, params: dict) -> str:
        """Generate signature for MEXC API requests."""
        query_string = '&'.join([f"{key}={params[key]}" for key in sorted(params.keys())])
        signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch klines data from MEXC asynchronously."""
        try:
            # Преобразуем timeframe в формат MEXC
            interval_map = {
                '1m': '1m',
                '5m': '5m',
                '15m': '15m',
                '30m': '30m',
                '1h': '60m',
                '4h': '4h',
                '1d': '1d'
            }
            interval = interval_map.get(timeframe, '60m')

            # Параметры запроса
            params = {
                'symbol': symbol.replace('/', ''),
                'interval': interval,
                'limit': limit
            }

            # Асинхронный запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v3/klines", params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

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
                for kline in data
            ]

            logger.info(f"Fetched {len(klines)} klines for {symbol} from MEXC")
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from MEXC: {str(e)}")
            raise

    async def get_symbols(self) -> list:
        """Fetch available trading symbols from MEXC asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v3/exchangeInfo") as response:
                    response.raise_for_status()
                    data = await response.json()

            symbols = [symbol['symbol'].replace('_', '/') for symbol in data['symbols'] if symbol['status'] == '1']
            logger.info(f"Fetched {len(symbols)} symbols from MEXC")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from MEXC: {str(e)}")
            raise
