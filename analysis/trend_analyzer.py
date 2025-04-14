from utils.logging_setup import setup_logging

logger = setup_logging('trend_analyzer')

class TrendAnalyzer:
    def __init__(self):
        pass

    def analyze(self, klines):
        """Analyze trend direction based on klines."""
        try:
            closes = [kline[4] for kline in klines]  # Close price is the 5th element
            if len(closes) < 5:
                return "neutral"
            avg_short = sum(closes[-5:]) / 5
            avg_long = sum(closes[-20:]) / 20 if len(closes) >= 20 else avg_short
            trend = "bullish" if avg_short > avg_long else "bearish" if avg_short < avg_long else "neutral"
            logger.info(f"Trend: {trend}")
            return trend
        except Exception as e:
            logger.error(f"Failed to analyze trend: {str(e)}")
            return "neutral"
