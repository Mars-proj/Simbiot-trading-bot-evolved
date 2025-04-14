from utils.logging_setup import setup_logging

logger = setup_logging('trade_logger')

class TradeLogger:
    def __init__(self):
        pass

    def log_trade(self, trade):
        logger.info(f"Logging trade: {trade}")
