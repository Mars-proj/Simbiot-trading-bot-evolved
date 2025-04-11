from trading_bot.logging_setup import setup_logging
from trading_bot.analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('risk_calculator')

class RiskCalculator:
    def __init__(self, market_state: dict, max_risk: float = 0.02):
        self.volatility = market_state['volatility']
        self.max_risk = max_risk
        self.analyzer = VolatilityAnalyzer(market_state)

    def calculate_position_size(self, klines: list, entry_price: float, stop_loss: float, account_balance: float) -> float:
        """Calculate position size based on risk parameters."""
        try:
            if not klines:
                logger.warning("No kline data provided for risk calculation")
                return 0.0

            # Анализируем волатильность
            market_volatility = self.analyzer.analyze_volatility(klines)
            
            # Динамическая корректировка риска на основе волатильности
            adjusted_risk = self.max_risk * (1 - self.volatility / 2)
            
            # Рассчитываем риск на сделку
            risk_per_trade = account_balance * adjusted_risk
            price_diff = abs(entry_price - stop_loss)
            
            if price_diff == 0:
                logger.warning("Price difference is zero, cannot calculate position size")
                return 0.0
            
            position_size = risk_per_trade / price_diff
            logger.info(f"Calculated position size: {position_size} (risk: {risk_per_trade}, volatility: {market_volatility})")
            return position_size
        except Exception as e:
            logger.error(f"Failed to calculate position size: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    calculator = RiskCalculator(market_state)
    klines = [{'close': float(50000 + i * 100)} for i in range(10)]
    position_size = calculator.calculate_position_size(klines, 50000, 49000, 10000)
    print(f"Position size: {position_size}")
