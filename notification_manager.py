from trading_bot.logging_setup import setup_logging
from trading_bot.utils.telegram_notifier import TelegramNotifier

logger = setup_logging('notification_manager')

class NotificationManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.notifier = TelegramNotifier(market_state)

    def notify(self, message: str, channel: str = 'telegram'):
        """Send a notification through the specified channel."""
        try:
            if channel != 'telegram':
                raise ValueError(f"Unsupported notification channel: {channel}")

            # Динамическая корректировка сообщения на основе волатильности
            if self.volatility > 0.5:
                message += f" (High volatility warning: {self.volatility})"

            self.notifier.notify(message)
            logger.info(f"Notification sent: {message}")
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    manager = NotificationManager(market_state)
    manager.notify("Test notification message")
