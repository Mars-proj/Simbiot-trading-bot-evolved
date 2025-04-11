import os
from dotenv import load_dotenv
from trading_bot.logging_setup import setup_logging

logger = setup_logging('config_loader')

def load_config(market_state: dict = None):
    """Load configuration from environment variables with dynamic adjustments."""
    try:
        load_dotenv()
        volatility = market_state['volatility'] if market_state else 0.0
        config = {
            "use_gpu": os.getenv("USE_GPU", "true") == "true",
            "cuda_visible_devices": os.getenv("CUDA_VISIBLE_DEVICES", "0"),
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", 6379)),
            "redis_db": int(os.getenv("REDIS_DB", 0)),
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
            "default_symbols": os.getenv("DEFAULT_SYMBOLS", "BTC/USDT,ETH/USDT").split(","),
            # Динамическая частота запросов: уменьшаем при высокой волатильности
            "api_requests_per_second": int(os.getenv("API_REQUESTS_PER_SECOND", 10)) * (1 - volatility / 2)
        }
        logger.info(f"Loaded configuration: {config}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    config = load_config(market_state)
    print(f"Configuration: {config}")
