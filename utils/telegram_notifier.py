import requests
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.config_loader import load_config

logger = setup_logging('telegram_notifier')

class TelegramNotifier:
    def __init__(self, market_state: dict):
        config = load_config(market_state)
        self.bot_token = config['telegram_bot_token']
        self.chat_id = config['telegram_chat_id']
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def notify(self, message: str):
        """Send a notification to Telegram."""
        try:
            if not self.bot_token or not self.chat_id:
                raise ValueError("Telegram bot token or chat ID not configured")
            payload = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(self.base_url, json=payload)
            if response.status_code != 200:
                raise ValueError(f"Failed to send Telegram message: {response.text}")
            logger.info(f"Sent Telegram notification: {message}")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    notifier = TelegramNotifier(market_state)
    notifier.notify("Test notification from trading bot")
