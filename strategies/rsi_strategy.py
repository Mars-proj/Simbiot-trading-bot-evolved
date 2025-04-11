from trading_bot.logging_setup import setup_logging
from trading_bot.analysis.technical_indicators import TechnicalIndicators

logger = setup_logging('rsi_strategy')

class RSIStrategy:
    def __init__(self, market_state: dict, period: int = 14, overbought: float = 70, oversold: float = 30):
        self.volatility = market_state['volatility']
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.indicators = TechnicalIndicators(market_state)

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using RSI strategy."""
        try:
            if len(klines) < self.period + 1:
                logger.warning("Not enough kline data for RSI strategy")
                return []

            # Рассчитываем RSI
            rsi = self.indicators.calculate_rsi(klines, self.period)
            
            # Динамические уровни перекупленности/перепроданности на основе волатильности
            adjusted_overbought = self.overbought - (self.volatility * 10)
            adjusted_oversold = self.oversold + (self.volatility * 10)
            
            signals = []
            for i in range(len(klines)):
                if rsi > adjusted_overbought:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'sell'})
                elif rsi < adjusted_oversold:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
                else:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} RSI signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate RSI signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = RSIStrategy(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(20)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")
