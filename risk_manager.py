from trading_bot.logging_setup import setup_logging
from trading_bot.trading.risk_calculator import RiskCalculator

logger = setup_logging('risk_manager')

class RiskManager:
    def __init__(self, market_state: dict, max_risk_per_trade: float = 0.02):
        self.volatility = market_state['volatility']
        self.max_risk_per_trade = max_risk_per_trade
        self.risk_calculator = RiskCalculator(market_state, max_risk_per_trade)

    def assess_risk(self, klines: list, entry_price: float, stop_loss: float, account_balance: float) -> dict:
        """Assess risk for a trade."""
        try:
            # Рассчитываем размер позиции
            position_size = self.risk_calculator.calculate_position_size(
                klines, entry_price, stop_loss, account_balance
            )

            # Динамическая корректировка риска на основе волатильности
            adjusted_risk = self.max_risk_per_trade * (1 - self.volatility / 2)
            risk_amount = account_balance * adjusted_risk

            risk_assessment = {
                'position_size': position_size,
                'risk_amount': risk_amount,
                'is_safe': position_size * (entry_price - stop_loss) <= risk_amount
            }

            logger.info(f"Risk assessment: {risk_assessment}")
            return risk_assessment
        except Exception as e:
            logger.error(f"Failed to assess risk: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    manager = RiskManager(market_state)
    klines = [{'close': float(50000 + i * 100)} for i in range(10)]
    assessment = manager.assess_risk(klines, 50000, 49000, 10000)
    print(f"Risk assessment: {assessment}")
