import asyncio
import aiohttp
from trading_bot.logging_setup import setup_logging
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
                '1m': 'Min1',
                '5m': 'Min5',
                '15m': 'Min15',
                '30m': 'Min30',
                '1h': 'Hour1',
                '4h': 'Hour4',
                '1d': 'Day1'
            }
            interval = interval_map.get(timeframe, 'Hour1')

            # Параметры запроса
            params = {
                'symbol': symbol.replace('/', ''),  # MEXC использует формат, например, BTCUSDT
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

            symbols = [symbol['symbol'].replace('_', '/') for symbol in data['symbols'] if symbol['status'] == 'ENABLED']
            logger.info(f"Fetched {len(symbols)} symbols from MEXC")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from MEXC: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    mexc_api = MEXCAPI(market_state)
    
    # Тестируем асинхронные методы
    async def main():
        symbols = await mexc_api.get_symbols()
        print(f"Available symbols: {symbols[:5]}")  # Первые 5 символов
        
        klines = await mexc_api.get_klines("BTC/USDT", "1h", 5)
        print(f"Klines for BTC/USDT: {klines}")

    asyncio.run(main())
