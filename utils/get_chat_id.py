import requests
from trading_bot.logging_setup import setup_logging

logger = setup_logging('get_chat_id')

def get_chat_id(token: str) -> str:
    """Get the chat ID for Telegram notifications."""
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data['ok'] and data['result']:
            chat_id = data['result'][0]['message']['chat']['id']
            logger.info(f"Successfully retrieved chat ID: {chat_id}")
            return str(chat_id)
        else:
            logger.error("No chat ID found in Telegram updates")
            raise ValueError("No chat ID found in Telegram updates")
    except Exception as e:
        logger.error(f"Failed to get chat ID: {str(e)}")
        raise

if __name__ == "__main__":
    # Test run
    # Replace 'your_telegram_bot_token' with your actual Telegram bot token
    token = "your_telegram_bot_token"
    chat_id = get_chat_id(token)
    print(f"Chat ID: {chat_id}")

