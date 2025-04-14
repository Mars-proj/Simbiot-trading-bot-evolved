import ccxt.async_support as ccxt
from utils.logging_setup import setup_logging

logger = setup_logging('trade_executor')

class TradeExecutor:
    def __init__(self, exchange_name="mexc"):
        self.exchange_name = exchange_name
        self.exchange = ccxt.mexc({
            'enableRateLimit': True,
            'apiKey': os.getenv('MEXC_API_KEY'),  # Укажи свои API-ключи в переменных окружения
            'secret': os.getenv('MEXC_API_SECRET'),
        })
        logger.info(f"TradeExecutor initialized for {exchange_name}")

    async def execute(self, signal):
        """Execute a trade asynchronously."""
        try:
            symbol = signal['symbol']
            side = signal['signal']  # "buy" или "sell"
            amount = signal['trade_size']
            price = signal['entry_price']

            # Размещаем ордер на бирже
            order = await self.exchange.create_limit_order(
                symbol=symbol,
                side=side,
                amount=amount,
                price=price
            )

            # Добавляем стоп-лосс, если указан
            if 'stop_loss' in signal:
                stop_loss_price = signal['stop_loss']
                stop_order = await self.exchange.create_order(
                    symbol=symbol,
                    type='stop_loss_limit',
                    side='sell' if side == 'buy' else 'buy',
                    amount=amount,
                    price=stop_loss_price,
                    params={'triggerPrice': stop_loss_price}
                )
                logger.info(f"Placed stop-loss order for {symbol}: {stop_order}")

            logger.info(f"Executed trade for {symbol}: {order}")
            return {"order_id": order['id'], "status": order['status']}
        except Exception as e:
            logger.error(f"Failed to execute trade for {symbol}: {str(e)}")
            return {"order_id": None, "status": "failed"}
        finally:
            await self.exchange.close()

    async def close(self):
        """Close the exchange connection."""
        try:
            await self.exchange.close()
            logger.info(f"Closed TradeExecutor connection for {self.exchange_name}")
        except Exception as e:
            logger.error(f"Failed to close TradeExecutor connection: {str(e)}")
