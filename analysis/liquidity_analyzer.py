from utils.logging_setup import setup_logging

logger = setup_logging('liquidity_analyzer')

class LiquidityAnalyzer:
    def __init__(self):
        self.min_liquidity = 100

    def analyze(self, symbol, klines):
        """Analyze liquidity based on volume in klines."""
        try:
            volumes = [kline[5] for kline in klines]  # Volume is the 6th element in klines
            avg_volume = sum(volumes) / len(volumes) if volumes else 0
            logger.info(f"Average volume for {symbol}: {avg_volume}")
            return avg_volume >= self.min_liquidity
        except Exception as e:
            logger.error(f"Failed to analyze liquidity for {symbol}: {str(e)}")
            return False
