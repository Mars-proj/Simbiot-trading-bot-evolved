from exchange_factory import ExchangeFactory
from strategy_manager import StrategyManager
from data_utils import load_historical_data, preprocess_data
from notification_manager import notify
from celery_app import trade_execution_task
from monitoring import PerformanceMonitor
from logging_setup import setup_logging

logger = setup_logging('core')

class TradingBot:
    def __init__(self, exchange_id: str, symbols: list):
        self.exchange = ExchangeFactory.create_exchange(exchange_id)
        self.strategy_manager = StrategyManager(exchange_id)
        self.symbols = symbols
        self.running = False
        self.monitor = PerformanceMonitor({"cpu": 80, "memory": 80})

    def start(self):
        self.running = True
        logger.info("Trading bot started")
        notify("Trading bot started", channel="telegram")
        while self.running:
            try:
                # Monitor performance
                self.monitor.monitor()

                # Filter symbols
                filtered_symbols = self.strategy_manager.filter_symbols(self.symbols)
                logger.info(f"Filtered symbols: {filtered_symbols}")

                for symbol in filtered_symbols:
                    # Load and preprocess data
                    data = load_historical_data(self.exchange.id, symbol, '1h', limit=100)
                    data = preprocess_data(data)

                    # Generate signals
                    signals = self.strategy_manager.generate_signals(data)
                    logger.info(f"Signals for {symbol}: {signals}")

                    # Execute trades asynchronously
                    for signal in signals:
                        if signal in ["buy", "sell"]:
                            trade_execution_task.delay(symbol, signal, 0.001)
                            logger.info(f"Scheduled {signal} trade for {symbol}")
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                notify(f"Error in trading bot: {str(e)}", channel="telegram")

    def stop(self):
        self.running = False
        logger.info("Trading bot stopped")
        notify("Trading bot stopped", channel="telegram")

    def get_status(self):
        return "running" if self.running else "stopped"
