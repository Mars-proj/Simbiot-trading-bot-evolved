import requests
from trading_bot.logging_setup import setup_logging
from .get_chat_id import get_chat_id

logger = setup_logging('telegram_notifier')

class TelegramNotifier:
    def __init__(self, market_state: dict, token: str = None, chat_id: str = None):
        self.volatility = market_state['volatility']
        self.token = token
        self.chat_id = chat_id or (self.token and get_chat_id(self.token))

    def notify(self, message: str) -> None:
        """Send a notification via Telegram."""
        try:
            if not self.token or not self.chat_id:
                raise ValueError("Token and chat ID must be provided for Telegram notifications")
                
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            params = {
                'chat_id': self.chat_id,
                'text': message
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            logger.info(f"Telegram notification sent: {message}")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    # Replace 'your_telegram_bot_token' and 'your_chat_id' with your actual Telegram bot token and chat ID
    market_state = {'volatility': 0.3}
    token = "your_telegram_bot_token"
    chat_id = "your_chat_id"
    notifier = TelegramNotifier(market_state, token, chat_id)
    notifier.notify("Test notification")
