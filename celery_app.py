from celery import Celery
from logging_setup import setup_logging

logger = setup_logging('celery_app')

app = Celery('trading_bot', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def trade_execution_task(symbol: str, signal: str, amount: float, exchange: dict, api_key: str, api_secret: str):
    """Execute a trade on the exchange."""
    try:
        logger.info(f"Executing trade: symbol={symbol}, signal={signal}, amount={amount}")

        # Reconstruct exchange object
        import ccxt
        exchange_class = getattr(ccxt, exchange['id'])
        exchange_obj = exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
        })

        # Execute trade
        if signal == "buy":
            order = exchange_obj.create_market_buy_order(symbol, amount)
        elif signal == "sell":
            order = exchange_obj.create_market_sell_order(symbol, amount)

        logger.info(f"Trade executed: {signal} {amount} of {symbol}, order: {order}")
    except Exception as e:
        logger.error(f"Failed to execute trade: {str(e)}")
        raise
