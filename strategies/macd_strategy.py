from trading_bot.logging_setup import setup_logging
import numpy as np

logger = setup_logging('macd_strategy')

class MACDStrategy:
    def __init__(self, market_state: dict, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.volatility = market_state['volatility']
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate_ema(self, prices: list, period: int) -> list:
        """Calculate Exponential Moving Average (EMA)."""
        ema = []
        k = 2 / (period + 1)
        ema.append(prices[0])  # Первое значение — это просто цена
        for i in range(1, len(prices)):
            ema.append(prices[i] * k + ema[-1] * (1 - k))
        return ema

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using MACD strategy."""
        try:
            if len(klines) < self.slow_period + self.signal_period:
                logger.warning("Not enough kline data for MACD strategy")
                return []

            closes = [float(kline['close']) for kline in klines]
            
            # Корректировка данных на основе волатильности
            adjusted_closes = [close * (1 + self.volatility / 2) for close in closes]
            
            # Рассчитываем EMA
            ema_fast = self.calculate_ema(adjusted_closes, self.fast_period)
            ema_slow = self.calculate_ema(adjusted_closes, self.slow_period)
            
            # Рассчитываем MACD
            macd = [fast - slow for fast, slow in zip(ema_fast, ema_slow)]
            
            # Рассчитываем сигнальную линию
            signal_line = self.calculate_ema(macd, self.signal_period)
            
            signals = []
            for i in range(self.slow_period + self.signal_period - 1, len(klines)):
                macd_value = macd[i]
                signal_value = signal_line[i - (self.slow_period - 1)]
                
                if macd_value > signal_value:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
                elif macd_value < signal_value:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'sell'})
                else:
                    signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} MACD signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate MACD signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = MACDStrategy(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(40)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")
