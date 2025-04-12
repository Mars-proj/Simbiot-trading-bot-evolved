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

logger = setup_logging('kucoin_api')

class KuCoinAPI:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.api_key = os.getenv('KUCOIN_API_KEY')
        self.api_secret = os.getenv('KUCOIN_API_SECRET')
        self.api_passphrase = os.getenv('KUCOIN_API_PASSPHRASE')
        self.base_url = "https://api.kucoin.com"

        # Проверяем, что ключи загружены
        if not self.api_key or not self.api_secret or not self.api_passphrase:
            logger.error("KuCoin API keys not found in .env file")
            raise ValueError("KuCoin API keys not found in .env file")

    def _generate_signature(self, method: str, path: str, params: dict, timestamp: str) -> str:
        """Generate signature for KuCoin API requests."""
        query_string = '&'.join([f"{key}={params[key]}" for key in sorted(params.keys())]) if params else ''
        message = f"{timestamp}{method}{path}{query_string}"
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch klines data from KuCoin asynchronously."""
        try:
            # Преобразуем timeframe в формат KuCoin
            interval_map = {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '1h': '1hour',
                '4h': '4hour',
                '1d': '1day'
            }
            interval = interval_map.get(timeframe, '1hour')

            # Параметры запроса
            symbol = symbol.replace('/', '-').upper()  # KuCoin использует формат, например, BTC-USDT
            params = {
                'symbol': symbol,
                'type': interval,
                'limit': limit
            }

            # Асинхронный запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/market/candles", params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            if data['code'] != '200000':
                raise Exception(data['msg'])

            # Преобразуем данные в формат, ожидаемый системой
            klines = [
                {
                    'timestamp': int(kline[0]),
                    'open': float(kline[1]),
                    'close': float(kline[2]),
                    'high': float(kline[3]),
                    'low': float(kline[4]),
                    'volume': float(kline[5])
                }
                for kline in data['data']
            ]

            logger.info(f"Fetched {len(klines)} klines for {symbol} from KuCoin")
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from KuCoin: {str(e)}")
            raise

    async def get_symbols(self) -> list:
        """Fetch available trading symbols from KuCoin asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/v1/symbols") as response:
                    response.raise_for_status()
                    data = await response.json()

            if data['code'] != '200000':
                raise Exception(data['msg'])

            symbols = [symbol['symbol'].replace('-', '/') for symbol in data['data'] if symbol['enableTrading']]
            logger.info(f"Fetched {len(symbols)} symbols from KuCoin")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from KuCoin: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    kucoin_api = KuCoinAPI(market_state)
    
    async def main():
        symbols = await kucoin_api.get_symbols()
        print(f"Available symbols: {symbols[:5]}")  # Первые 5 символов
        
        klines = await kucoin_api.get_klines("BTC/USDT", "1h", 5)
        print(f"Klines for BTC/USDT: {klines}")

    asyncio.run(main())
