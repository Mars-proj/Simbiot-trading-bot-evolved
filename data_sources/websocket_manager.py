import asyncio
import websockets
from trading_bot.logging_setup import setup_logging

logger = setup_logging('websocket_manager')

class WebSocketManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.websocket_urls = {
            'binance': 'wss://stream.binance.com:9443/ws',
            'kraken': 'wss://ws.kraken.com',
            'mexc': 'wss://wbs.mexc.com/ws'
        }
        self.subscriptions = {}

    async def connect(self, exchange_name: str, symbol: str, callback) -> None:
        """Connect to the WebSocket of the specified exchange and stream data."""
        try:
            if exchange_name not in self.websocket_urls:
                logger.error(f"Unsupported exchange for WebSocket: {exchange_name}")
                raise ValueError(f"Unsupported exchange: {exchange_name}")

            url = self.websocket_urls[exchange_name]
            symbol = symbol.replace('/', '').lower()

            # Формируем подписку в зависимости от биржи
            if exchange_name == 'binance':
                subscription = f"{symbol}@kline_1h"
            elif exchange_name == 'kraken':
                subscription = {"event": "subscribe", "pair": [symbol.upper()], "subscription": {"name": "ohlc", "interval": 60}}
            elif exchange_name == 'mexc':
                subscription = {"method": "SUBSCRIPTION", "params": [f"spot@public.kline@{symbol}@1h"]}

            self.subscriptions[symbol] = subscription

            async with websockets.connect(url) as websocket:
                # Отправляем подписку
                await websocket.send(json.dumps(subscription))
                logger.info(f"Subscribed to {symbol} on {exchange_name}")

                # Обрабатываем входящие сообщения
                while True:
                    message = await websocket.recv()
                    data = json.loads(message)
                    await callback(data)
        except Exception as e:
            logger.error(f"WebSocket error for {symbol} on {exchange_name}: {str(e)}")
            raise

    async def stream_klines(self, symbol: str, exchange_name: str, callback) -> None:
        """Stream klines data from the specified exchange."""
        await self.connect(exchange_name, symbol, callback)

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    ws_manager = WebSocketManager(market_state)

    async def handle_message(message):
        print(f"Received message: {message}")

    async def main():
        await ws_manager.stream_klines("BTC/USDT", "mexc", handle_message)

    asyncio.run(main())
