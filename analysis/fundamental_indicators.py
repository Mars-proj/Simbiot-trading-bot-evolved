from trading_bot.logging_setup import setup_logging

logger = setup_logging('fundamental_indicators')

class FundamentalIndicators:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def calculate_pe_ratio(self, price: float, earnings: float) -> float:
        """Calculate Price-to-Earnings (P/E) ratio."""
        try:
            if earnings == 0:
                logger.warning("Earnings are zero, cannot calculate P/E ratio")
                return 0.0

            # Корректировка цены на основе волатильности
            adjusted_price = price * (1 + self.volatility / 2)
            pe_ratio = adjusted_price / earnings
            logger.info(f"Calculated P/E ratio: {pe_ratio}")
            return pe_ratio
        except Exception as e:
            logger.error(f"Failed to calculate P/E ratio: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    indicators = FundamentalIndicators(market_state)
    pe_ratio = indicators.calculate_pe_ratio(50000, 1000)
    print(f"P/E Ratio: {pe_ratio}")
