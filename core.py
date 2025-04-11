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
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange, self.exchange_id = ExchangeFactory.create_exchange(api_key, api_secret)
        self.strategy_manager = StrategyManager(self.exchange_id)
        self.symbols = symbols
        self.running = False
        self.monitor = PerformanceMonitor({"cpu": 80, "memory": 80})

    def calculate_trade_amount(self, symbol: str, market_state: dict) -> float:
        """Calculate the trade amount dynamically based on market conditions."""
        try:
            # Fetch current price of the symbol
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']

            # Calculate minimum trade amount (10 USD + commission)
            min_usd_amount = 10.0  # Minimum order in USD
            commission_rate = 0.001  # Assume 0.1% commission for MEXC
            min_usd_amount_with_commission = min_usd_amount * (1 + commission_rate)  # ~10.01 USD
            min_amount = min_usd_amount_with_commission / current_price  # Convert to asset amount

            # Calculate maximum trade amount based on market state
            # Use volatility, order book imbalance, and account balance
            volatility = market_state['volatility']
            order_book_imbalance = market_state['order_book_imbalance']

            # Fetch account balance
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['free'].get('USDT', 0.0)

            # Dynamic max amount: scale based on volatility and balance
            # Lower volatility -> higher trade amount; higher volatility -> lower trade amount
            volatility_factor = max(0.1, min(1.0, 1.0 / (volatility + 0.01)))  # Avoid division by zero
            max_usdt_amount = usdt_balance * 0.1 * volatility_factor  # Use 10% of balance, scaled by volatility

            # Adjust max amount based on order book imbalance
            # If buy pressure is high (positive imbalance), increase amount for buy; if sell pressure is high, increase for sell
            imbalance_factor = 1.0 + abs(order_book_imbalance) * 0.5
            max_usdt_amount *= imbalance_factor

            # Convert max USD amount to asset amount
            max_amount = max_usdt_amount / current_price

            # Ensure the amount is between min and max
            trade_amount = max(min_amount, min(max_amount, max_usdt_amount / current_price))

            # Round to the nearest valid amount (e.g., MEXC requires 5 decimal places for BTC)
            trade_amount = round(trade_amount, 5)

            logger.info(f"Calculated trade amount for {symbol}: {trade_amount} (min: {min_amount}, max: {max_amount})")
            return trade_amount
        except Exception as e:
            logger.error(f"Failed to calculate trade amount for {symbol}: {str(e)}")
            raise

    def start(self):
        self.running = True
        logger.info(f"Trading bot started on {self.exchange_id}")
        notify(f"Trading bot started on {self.exchange_id}", channel="telegram")
        while self.running:
            try:
                # Monitor performance
                self.monitor.monitor()

                # Analyze market state for dynamic filtering
                data = load_historical_data(self.exchange, 'BTC/USDT', '1h', {'volatility': 0.02}, limit=100)
                market_state = self.strategy_manager.generate_signals(data, self.exchange)

                # Filter symbols
                filtered_symbols = self.strategy_manager.filter_symbols(self.symbols, self.exchange, market_state)
                logger.info(f"Filtered symbols: {filtered_symbols}")

                for symbol in filtered_symbols:
                    # Load and preprocess data
                    data = load_historical_data(self.exchange, symbol, '1h', market_state, limit=100)
                    data = preprocess_data(data)

                    # Generate signals
                    signals = self.strategy_manager.generate_signals(data, self.exchange)
                    logger.info(f"Signals for {symbol}: {signals}")

                    # Execute trades asynchronously
                    for signal in signals:
                        if signal in ["buy", "sell"]:
                            # Calculate dynamic trade amount
                            trade_amount = self.calculate_trade_amount(symbol, market_state)
                            trade_execution_task.delay(symbol, signal, trade_amount, self.exchange.__dict__, self.api_key, self.api_secret)
                            logger.info(f"Scheduled {signal} trade for {symbol} with amount {trade_amount}")
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                notify(f"Error in trading bot: {str(e)}", channel="telegram")

    def stop(self):
        self.running = False
        logger.info("Trading bot stopped")
        notify("Trading bot stopped", channel="telegram")

    def get_status(self):
        return "running" if self.running else "stopped"
