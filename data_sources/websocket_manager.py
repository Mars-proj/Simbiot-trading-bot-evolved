from trading_bot.logging_setup import setup_logging
import ccxt.async_support as ccxt_async
import asyncio

logger = setup_logging('websocket_manager')

class WebsocketManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.exchange = ccxt_async.binance({
            'enableRateLimit': True,
        })

    async def subscribe(self, symbol: str, callback):
        """Subscribe to real-time data for a symbol via WebSocket."""
        try:
            await self.exchange.load_markets()
            if symbol not in self.exchange.markets:
                logger.warning(f"Symbol {symbol} not available on Binance")
                return

            logger.info(f"Subscribing to {symbol} via WebSocket")
            while True:
                try:
                    ticker = await self.exchange.watch_ticker(symbol)
                    # Динамическая корректировка цены на основе волатильности
                    adjusted_price = ticker['last'] * (1 - self.volatility / 2)
                    await callback({
                        'symbol': symbol,
                        'price': adjusted_price,
                        'timestamp': ticker['timestamp'] // 1000
                    })
                except Exception as e:
                    logger.error(f"WebSocket error for {symbol}: {str(e)}")
                    await asyncio.sleep(5)  # Пауза перед повторной попыткой
        except Exception as e:
            logger.error(f"Failed to subscribe to {symbol}: {str(e)}")
            raise
        finally:
            await self.exchange.close()

if __name__ == "__main__":
    # Test run
    async def on_message(data):
        print(f"Received: {data}")

    market_state = {'volatility': 0.3}
    manager = WebsocketManager(market_state)
    symbols = manager.exchange.load_markets().keys()
    symbol = next((s for s in symbols if s.endswith('/USDT')), None)
    
    if symbol:
        asyncio.run(manager.subscribe(symbol, on_message))
    else:
        print("No USDT symbols available for testing")
