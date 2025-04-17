import asyncio
import asyncpg
import redis.asyncio as redis
import pandas as pd
import zipfile
import os
import json
from datetime import datetime, timedelta
from loguru import logger
from ccxt.async_support import Exchange

class DealPool:
    def __init__(self, db_config: dict, redis_config: dict, archive_dir: str = "archives"):
        """Initialize DealPool for managing trades."""
        self.db_config = db_config
        self.redis_config = redis_config
        self.archive_dir = archive_dir
        self.pool = None
        self.redis = None
        os.makedirs(archive_dir, exist_ok=True)
        logger.info("DealPool initialized with archive directory: {}", archive_dir)

    async def connect(self):
        """Connect to PostgreSQL and Redis."""
        self.pool = await asyncpg.create_pool(**self.db_config)
        self.redis = redis.Redis(**self.redis_config)
        logger.info("Connected to PostgreSQL and Redis")

    async def disconnect(self):
        """Close connections."""
        if self.pool:
            await self.pool.close()
        if self.redis:
            await self.redis.close()
        logger.info("Disconnected from PostgreSQL and Redis")

    async def save_trade(self, exchange: Exchange, trade: dict):
        """Save trade to PostgreSQL and Redis."""
        trade_id = trade["id"]
        trade_data = {
            "id": trade_id,
            "exchange": exchange.name,
            "symbol": trade["symbol"],
            "amount": trade["amount"],
            "price": trade["price"],
            "side": trade["side"],
            "timestamp": pd.to_datetime(trade["timestamp"], unit="ms").isoformat(),  # Convert to ISO string
            "fee": trade.get("fee", 0.0),
        }

        # Save to PostgreSQL
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO trades (id, exchange, symbol, amount, price, side, timestamp, fee)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (id) DO NOTHING
                """,
                trade_data["id"],
                trade_data["exchange"],
                trade_data["symbol"],
                trade_data["amount"],
                trade_data["price"],
                trade_data["side"],
                pd.to_datetime(trade_data["timestamp"]),  # Convert back to datetime for PostgreSQL
                trade_data["fee"],
            )

        # Cache in Redis (expire after 1 hour)
        await self.redis.setex(f"trade:{trade_id}", 3600, json.dumps(trade_data))
        logger.info("Saved trade {} to PostgreSQL and Redis", trade_id)

    async def archive_old_trades(self, days: int = 30):
        """Archive trades older than specified days to ZIP."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        async with self.pool.acquire() as conn:
            trades = await conn.fetch(
                "SELECT * FROM trades WHERE timestamp < $1",
                cutoff_date
            )
            if not trades:
                logger.info("No trades to archive")
                return

            df = pd.DataFrame(trades)
            archive_name = f"{self.archive_dir}/trades_{cutoff_date.strftime('%Y%m%d')}.csv"
            df.to_csv(archive_name, index=False)

            zip_name = f"{archive_name}.zip"
            with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(archive_name, os.path.basename(archive_name))
            os.remove(archive_name)

            await conn.execute(
                "DELETE FROM trades WHERE timestamp < $1",
                cutoff_date
            )
            logger.info("Archived {} trades to {}", len(trades), zip_name)

    async def get_trade(self, trade_id: str) -> dict:
        """Retrieve trade from Redis or PostgreSQL."""
        trade = await self.redis.get(f"trade:{trade_id}")
        if trade:
            logger.info("Retrieved trade {} from Redis", trade_id)
            trade_data = json.loads(trade)
            trade_data["timestamp"] = pd.to_datetime(trade_data["timestamp"])  # Convert back to Timestamp
            return trade_data

        async with self.pool.acquire() as conn:
            trade = await conn.fetchrow(
                "SELECT * FROM trades WHERE id = $1",
                trade_id
            )
            if trade:
                logger.info("Retrieved trade {} from PostgreSQL", trade_id)
                trade_data = dict(trade)
                trade_data["timestamp"] = pd.to_datetime(trade_data["timestamp"])
                await self.redis.setex(f"trade:{trade_id}", 3600, json.dumps(trade_data))
                return trade_data
        logger.warning("Trade {} not found", trade_id)
        return None
