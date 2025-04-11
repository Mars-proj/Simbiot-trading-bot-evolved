from trading_bot.logging_setup import setup_logging
from trading_bot.utils.utils_utils import calculate_dynamic_threshold
import numpy as np

logger = setup_logging('grid_strategy')

class GridStrategy:
    def __init__(self, market_state: dict, grid_levels: int = 5, grid_spacing: float = 0.02):
        self.volatility = market_state['volatility']
        self.grid_levels = grid_levels
        self.grid_spacing = grid_spacing

    def generate_signals(self, klines: list) -> list:
        """Generate trading signals using Grid strategy."""
        try:
            if len(klines) < 2:
                logger.warning("Not enough kline data for Grid strategy")
                return []

            closes = [float(kline['close']) for kline in klines]
            current_price = closes[-1]
            
            # Динамический шаг сетки на основе волатильности
            adjusted_spacing = self.grid_spacing * (1 + self.volatility)
            
            # Определяем центральную цену (средняя за последние несколько свечей)
            center_price = np.mean(closes[-self.grid_levels:])
            
            # Создаём уровни сетки
            grid = [center_price * (1 + i * adjusted_spacing) for i in range(-self.grid_levels, self.grid_levels + 1)]
            
            signals = []
            for i in range(len(klines)):
                price = closes[i]
                for level in grid:
                    if price > level and price < level + adjusted_spacing:
                        signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'buy'})
                    elif price < level and price > level - adjusted_spacing:
                        signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'sell'})
                    else:
                        signals.append({'timestamp': klines[i]['timestamp'], 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} Grid strategy signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate Grid strategy signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    strategy = GridStrategy(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(10)]
    signals = strategy.generate_signals(klines)
    print(f"Signals: {signals}")y

