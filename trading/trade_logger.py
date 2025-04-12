from trading_bot.logging_setup import setup_logging
from trading_bot.utils.telegram_notifier import TelegramNotifier
from trading_bot.core import TradingBotCore
from trading_bot.symbol_filter import SymbolFilter
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('trade_logger')

class TradeLogger:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.notifier = TelegramNotifier(market_state)

    def log_trade(self, trade: dict) -> None:
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
    core = TradingBotCore(market_state)
    symbol_filter = SymbolFilter(market_state)
    market_data = MarketData(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        # Запускаем торговлю для получения реальной сделки
        trades = core.run_trading(symbols[0], 'bollinger', 10000, '1h', 30, 'binance')
        if trades:
            trade_logger.log_trade(trades[0])
        else:
            print(f"No trades executed for {symbols[0]}")
    else:
        print("No symbols available for testing")
