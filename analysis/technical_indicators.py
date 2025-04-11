from trading_bot.logging_setup import setup_logging
import numpy as np

logger = setup_logging('technical_indicators')

class TechnicalIndicators:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def calculate_rsi(self, klines: list, period: int = 14) -> float:
        """Calculate Relative Strength Index (RSI)."""
        try:
            if len(klines) < period + 1:
                logger.warning("Not enough kline data for RSI calculation")
                return 0.0

            closes = [float(kline['close']) for kline in klines]
            
            # Корректировка данных на основе волатильности
            adjusted_closes = [close * (1 + self.volatility / 2) for close in closes]
            
            gains = []
            losses = []
            for i in range(1, len(adjusted_closes)):
                diff = adjusted_closes[i] - adjusted_closes[i-1]
                if diff > 0:
                    gains.append(diff)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(diff))
            
            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period
            
            for i in range(period, len(gains)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            if avg_loss == 0:
                rs = 100
            else:
                rs = avg_gain / avg_loss
            
            rsi = 100 - (100 / (1 + rs))
            logger.info(f"Calculated RSI: {rsi}")
            return rsi
        except Exception as e:
            logger.error(f"Failed to calculate RSI: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    indicators = TechnicalIndicators(market_state)
    klines = [{'close': float(50000 + i * 100)} for i in range(20)]
    rsi = indicators.calculate_rsi(klines)
    print(f"RSI: {rsi}")
