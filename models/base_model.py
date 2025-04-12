from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
import numpy as np

logger = setup_logging('base_model')

class BaseModel:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)
        self.weights = None  # Простая линейная модель: y = w * x + b
        self.bias = 0.0

    def train(self, X: list, y: list) -> None:
        """Train a simple linear model with the given data."""
        try:
            if len(X) != len(y) or len(X) == 0:
                raise ValueError("Invalid input data for training")

            # Простая линейная регрессия через метод наименьших квадратов
            X = np.array(X).reshape(-1, 1)
            y = np.array(y)
            X_mean = np.mean(X)
            y_mean = np.mean(y)
            
            # Вычисляем веса
            numerator = np.sum((X - X_mean) * (y - y_mean))
            denominator = np.sum((X - X_mean) ** 2)
            self.weights = numerator / denominator if denominator != 0 else 0.0
            self.bias = y_mean - self.weights * X_mean

            logger.info(f"Model trained with weights: {self.weights}, bias: {self.bias}")
        except Exception as e:
            logger.error(f"Failed to train model: {str(e)}")
            raise

    def predict(self, X: list) -> list:
        """Make predictions using the trained model."""
        try:
            if self.weights is None:
                raise ValueError("Model is not trained")

            X = np.array(X).reshape(-1, 1)
            predictions = self.weights * X + self.bias
            return predictions.flatten().tolist()
        except Exception as e:
            logger.error(f"Failed to make predictions: {str(e)}")
            raise

    def update(self, new_data: dict) -> None:
        """Update the model with new data."""
        try:
            # Предполагаем, что new_data содержит 'price' и 'target'
            if 'price' not in new_data or 'target' not in new_data:
                raise ValueError("New data must contain 'price' and 'target'")

            X = [new_data['price']]
            y = [new_data['target']]
            
            # Динамическая корректировка на основе волатильности
            X = [x * (1 + self.volatility / 2) for x in X]
            y = [val * (1 + self.volatility / 2) for val in y]
            
            # Переобучаем модель
            self.train(X, y)
            logger.info(f"Model updated with new data: {new_data}")
        except Exception as e:
            logger.error(f"Failed to update model: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    model = BaseModel(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(model.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        # Получаем данные для обучения
        klines = model.market_data.get_klines(symbols[0], '1h', 30, 'binance')
        X = [kline['close'] for kline in klines[:-1]]  # Цены закрытия для обучения
        y = [kline['close'] for kline in klines[1:]]   # Следующие цены закрытия как целевые значения
        
        model.train(X, y)
        predictions = model.predict(X)
        print(f"Predictions for {symbols[0]}: {predictions}")
        
        # Обновляем модель с новыми данными
        new_data = {
            'price': klines[-1]['close'],
            'target': klines[-1]['close'] * 1.01  # Предполагаем небольшой рост
        }
        model.update(new_data)
    else:
        print("No symbols available for testing")
