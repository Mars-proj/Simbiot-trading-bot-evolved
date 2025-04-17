import asyncio
from src.modules.tradepool.deal_pool import DealPool
from ccxt.async_support import binance

async def test_deal_pool():
    db_config = {
        "host": "localhost",
        "database": "simbiot_trading",
        "user": "simbiot_user",
        "password": "secure_password"
    }
    redis_config = {
        "host": "localhost",
        "port": 6379,
        "db": 0
    }
    deal_pool = DealPool(db_config, redis_config)
    await deal_pool.connect()

    # Тестовая сделка
    trade = {
        "id": "test123",
        "symbol": "BTC/USDT",
        "amount": 0.1,
        "price": 60000.0,
        "side": "buy",
        "timestamp": 1697059200000,
        "fee": 0.001
    }
    exchange = binance()
    await deal_pool.save_trade(exchange, trade)

    # Проверка получения
    retrieved = await deal_pool.get_trade("test123")
    print("Retrieved trade:", retrieved)

    # Тест архивации
    await deal_pool.archive_old_trades(days=1)
    await deal_pool.disconnect()

asyncio.run(test_deal_pool())
