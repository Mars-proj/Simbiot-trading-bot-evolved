from utils.logging_setup import setup_logging

logger = setup_logging('risk_calculator')

class RiskCalculator:
    def __init__(self, volatility_analyzer):
        self.volatility_analyzer = volatility_analyzer

    def calculate_risk(self, signal, klines):
        """Calculate risk for a trade."""
        try:
            volatility = self.volatility_analyzer.analyze(klines)
            # Пример: увеличиваем риск в зависимости от волатильности
            risk = signal['trade_size'] * volatility * 100
            logger.info(f"Calculated risk for {signal['symbol']}: {risk}")
            return risk
        except Exception as e:
            logger.error(f"Failed to calculate risk for {signal['symbol']}: {str(e)}")
            return 0
