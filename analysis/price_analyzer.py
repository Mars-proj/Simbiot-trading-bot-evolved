from utils.logging_setup import setup_logging

logger = setup_logging('price_analyzer')

class PriceAnalyzer:
    def __init__(self):
        pass

    def analyze(self, klines):
        """Analyze price trends based on klines."""
        try:
            closes = [kline[4] for kline in klines]  # Close price is the 5th element
            if len(closes) < 2:
                return 0
            trend = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] != 0 else 0
            logger.info(f"Price trend: {trend}")
            return trend
        except Exception as e:
            logger.error(f"Failed to analyze price: {str(e)}")
            return 0
