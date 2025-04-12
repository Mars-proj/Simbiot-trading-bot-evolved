from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from .base_model import BaseModel
import numpy as np
import xgboost as xgb

logger = setup_logging('xgboost_model')

class XGBoostModel(BaseModel):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.model = None
        self.sequence_length = 10  # Длина последовательности для признаков

    def _prepare_features(self, klines: list) -> list:
        """Extract features from klines for XGBoost."""
        features = []
        for i in range(len(klines) - self.sequence_length):
            seq = klines[i:i + self.sequence_length]
            # Простые признаки: цены закрытия за последние sequence_length периодов
            feature = [kline['close'] for kline in seq]
            features.append(feature)
        return features

    def train(self, X: list, y: list) -> None:
        """Train the XGBoost model with the given data."""
        try:
            if len(X) != len(y) or len(X) == 0:
                raise ValueError("Invalid input data for XGBoost training")

            # Преобразуем данные в numpy массивы
            X = np.array(X)
            y = np.array(y)

            # Создаём и обучаем модель
            self.model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, learning_rate=0.1)
            self.model.fit(X, y)
            logger.info("XGBoost model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train XGBoost model: {str(e)}")
            raise

    def predict(self, X: list) -> list:
        """Make predictions using the trained XGBoost model."""
        try:
            if self.model is None:
                raise ValueError("XGBoost model is not trained")

            X = np.array(X)
            predictions = self.model.predict(X)
            return predictions.tolist()
        except Exception as e:
            logger.error(f"Failed to make XGBoost predictions: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    model = XGBoostModel(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(model.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        # Получаем данные для обучения
        klines = model.market_data.get_klines(symbols[0], '1h', 50, 'binance')
        X = model._prepare_features(klines[:-1])  # Признаки для обучения
        y = [kline['close'] for kline in klines[model.sequence_length:]]  # Целевые значения
        
        model.train(X, y)
        predictions = model.predict(X)
        print(f"XGBoost Predictions for {symbols[0]}: {predictions}")
    else:
        print("No symbols available for testing")
