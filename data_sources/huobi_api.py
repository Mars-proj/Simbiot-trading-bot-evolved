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
import urllib.parse

# Загружаем переменные из .env
load_dotenv()

logger = setup_logging('huobi_api')

class HuobiAPI:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.api_key = os.getenv('HUOBI_API_KEY')
        self.api_secret = os.getenv('HUOBI_API_SECRET')
        self.base_url = "https://api.huobi.pro"

        # Проверяем, что ключи загружены
        if not self.api_key or not self.api_secret:
            logger.error("Huobi API keys not found in .env file")
            raise ValueError("Huobi API keys not found in .env file")

    def _generate_signature(self, method: str, path: str, params: dict) -> str:
        """Generate signature for Huobi API requests."""
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        params.update({
            'AccessKeyId': self.api_key,
            'SignatureMethod': 'HmacSHA256',
            'SignatureVersion': '2',
            'Timestamp': timestamp
        })
        sorted_params = sorted(params.items())
        query_string = urllib.parse.urlencode(sorted_params)
        message = f"{method}\napi.huobi.pro\n{path}\n{query_string}"
        signature = hmac.new(self.api_secret.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')

    async def get_klines(self, symbol: str, timeframe: str, limit: int) -> list:
        """Fetch klines data from Huobi asynchronously."""
        try:
            # Преобразуем timeframe в формат Huobi
            interval_map = {
                '1m': '1min',
                '5m': '5min',
                '15m': '15min',
                '30m': '30min',
                '1h': '60min',
                '4h': '4hour',
                '1d': '1day'
            }
            interval = interval_map.get(timeframe, '60min')

            # Параметры запроса
            params = {
                'symbol': symbol.replace('/', '').lower(),  # Huobi использует формат, например, btcusdt
                'period': interval,
                'size': limit
            }

            # Асинхронный запрос
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/market/history/kline", params=params) as response:
                    response.raise_for_status()
                    data = await response.json()

            if data['status'] != 'ok':
                raise Exception(data['err-msg'])

            # Преобразуем данные в формат, ожидаемый системой
            klines = [
                {
                    'timestamp': int(kline['id']),
                    'open': float(kline['open']),
                    'high': float(kline['high']),
                    'low': float(kline['low']),
                    'close': float(kline['close']),
                    'volume': float(kline['vol'])
                }
                for kline in data['data']
            ]

            logger.info(f"Fetched {len(klines)} klines for {symbol} from Huobi")
            return klines
        except Exception as e:
            logger.error(f"Failed to fetch klines for {symbol} from Huobi: {str(e)}")
            raise

    async def get_symbols(self) -> list:
        """Fetch available trading symbols from Huobi asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v1/common/symbols") as response:
                    response.raise_for_status()
                    data = await response.json()

            if data['status'] != 'ok':
                raise Exception(data['err-msg'])

            symbols = [symbol['symbol'].replace('_', '/') for symbol in data['data'] if symbol['state'] == 'online']
            logger.info(f"Fetched {len(symbols)} symbols from Huobi")
            return symbols
        except Exception as e:
            logger.error(f"Failed to fetch symbols from Huobi: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    huobi_api = HuobiAPI(market_state)
    
    async def main():
        symbols = await huobi_api.get_symbols()
        print(f"Available symbols: {symbols[:5]}")  # Первые 5 символов
        
        klines = await huobi_api.get_klines("BTC/USDT", "1h", 5)
        print(f"Klines for BTC/USDT: {klines}")

    asyncio.run(main())
