from exchange_factory import ExchangeFactory
from strategy_manager import StrategyManager
from data_utils import load_historical_data, preprocess_data
import logging

def setup_logging():
    logging.basicConfig(
        filename='core.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class TradingBot:
    def __init__(self, exchange_id: str, symbols: list):
        self.exchange = ExchangeFactory.create_exchange(exchange_id)
        self.strategy_manager = StrategyManager(exchange_id)
        self.symbols = symbols
        self.running = False
        setup_logging()

    def start(self):
        self.running = True
        logging.info("Trading bot started")
        while self.running:
            try:
                # Filter symbols
                filtered_symbols = self.strategy_manager.filter_symbols(self.symbols)
                logging.info(f"Filtered symbols: {filtered_symbols}")

                for symbol in filtered_symbols:
                    # Load and preprocess data
                    data = load_historical_data(self.exchange.id, symbol, '1h', limit=100)
                    data = preprocess_data(data)

                    # Generate signals
                    signals = self.strategy_manager.generate_signals(data)
                    logging.info(f"Signals for {symbol}: {signals}")

                    # Execute trades based on the first signal (simplified)
                    for signal in signals:
                        if signal == "buy":
                            self.exchange.execute_trade({"symbol": symbol, "side": "buy", "amount": 0.001})
                            logging.info(f"Executed buy trade for {symbol}")
                        elif signal == "sell":
                            self.exchange.execute_trade({"symbol": symbol, "side": "sell", "amount": 0.001})
                            logging.info(f"Executed sell trade for {symbol}")
            except Exception as e:
                logging.error(f"Error in trading loop: {str(e)}")

    def stop(self):
        self.running = False
        logging.info("Trading bot stopped")

    def get_status(self):
        return "running" if self.running else "stopped"
