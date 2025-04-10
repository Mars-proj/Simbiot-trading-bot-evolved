import requests
from dotenv import load_dotenv
import os
from logging_setup import setup_logging

logger = setup_logging('telegram_notifier')

def send_telegram_message(message: str):
    """Send a message to Telegram."""
    try:
        # Load Telegram bot token and chat ID from .env
        load_dotenv()
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        if not bot_token or not chat_id:
            logger.error("Telegram bot token or chat ID not found in .env")
            raise ValueError("Telegram bot token or chat ID not found")

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Telegram message sent: {message}")
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {str(e)}")
        raise
