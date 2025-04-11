from trading_bot.logging_setup import setup_logging
from trading_bot.utils.telegram_notifier import TelegramNotifier

logger = setup_logging('trade_logger')

class TradeLogger:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.notifier = TelegramNotifier(market_state)

    def log_trade(self, trade: dict):
        """Log a trade and send a notification."""
        try:
            # Формируем сообщение о сделке
            message = f"Trade Executed: {trade['symbol']} | Side: {trade['side']} | Quantity: {trade['quantity']} | Price: {trade['entry_price']} | Status: {trade['status']}"
            
            # Логируем в файл
            logger.info(message)
            
            # Отправляем уведомление через Telegram
            self.notifier.notify(message)
            
            logger.info(f"Logged trade: {trade}")
        except Exception as e:
            logger.error(f"Failed to log trade: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    trade_logger = TradeLogger(market_state)
    trade = {
        'symbol': 'BTC/USDT',
        'side': 'buy',
        'quantity': 0.1,
        'entry_price': 50000,
        'status': 'open'
    }
    trade_logger.log_trade(trade)
