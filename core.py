from exchange_factory import ExchangeFactory
from strategy_manager import StrategyManager
from data_utils import load_historical_data, preprocess_data
from notification_manager import notify
from celery_app import trade_execution_task
from monitoring import PerformanceMonitor
from logging_setup import setup_logging

logger = setup_logging('core')

class TradingBot:
    def __init__(self, api_key: str, api_secret: str, symbols: list):
        self.exchange, self.exchange_id = ExchangeFactory.create_exchange(api_key, api_secret)
        self.strategy_manager = StrategyManager(self.exchange_id)
        self.symbols = symbols
        self.running = False
        self.monitor = PerformanceMonitor({"cpu": 80, "memory": 80})

    def start(self):
        self.running = True
        logger.info(f"Trading bot started on {self.exchange_id}")
        notify(f"Trading bot started on {self.exchange_id}", channel="telegram")
        while self.running:
            try:
                # Monitor performance
                self.monitor.monitor()

                # Filter symbols
                filtered_symbols = self.strategy_manager.filter_symbols(self.symbols)
                logger.info(f"Filtered symbols: {filtered_symbols}")

                for symbol in filtered_symbols:
                    # Load and preprocess data
                    data = load_historical_data(self.exchange, symbol, '1h', limit=100)
                    data = preprocess_data(data)

                    # Generate signals
                    signals = self.strategy_manager.generate_signals(data, self.exchange)
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
