import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.config_loader import load_config

logger = setup_logging('get_chat_id')

def get_chat_id(market_state: dict):
    """Get Telegram chat ID for notifications."""
    try:
        config = load_config(market_state)
        bot_token = config['telegram_bot_token']
        if not bot_token:
            raise ValueError("Telegram bot token not configured")
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        if response.status_code != 200:
            raise ValueError(f"Failed to get updates: {response.text}")
        updates = response.json()
        if not updates['ok'] or not updates['result']:
            raise ValueError("No updates found")
        chat_id = updates['result'][0]['message']['chat']['id']
        logger.info(f"Retrieved chat ID: {chat_id}")
        return chat_id
    except Exception as e:
        logger.error(f"Failed to get chat ID: {str(e)}")
        raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    chat_id = get_chat_id(market_state)
    print(f"Chat ID: {chat_id}")
