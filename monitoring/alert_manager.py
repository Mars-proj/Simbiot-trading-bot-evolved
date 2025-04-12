from trading_bot.logging_setup import setup_logging
from trading_bot.utils.telegram_notifier import TelegramNotifier

logger = setup_logging('alert_manager')

class AlertManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.notifier = TelegramNotifier(market_state)

    def send_alert(self, message: str, severity: str = 'info'):
        """Send an alert with the specified message."""
        try:
            # Динамическая корректировка сообщения на основе волатильности
            if self.volatility > 0.5 and severity == 'info':
                severity = 'warning'
                message += f" (High volatility detected: {self.volatility})"
            
            full_message = f"[{severity.upper()}] {message}"
            self.notifier.notify(full_message)
            logger.info(f"Alert sent: {full_message}")
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    manager = AlertManager(market_state)
    manager.send_alert("Test alert message")
