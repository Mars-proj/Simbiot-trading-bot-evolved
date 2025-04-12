from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from .base_model import BaseModel
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, MultiHeadAttention, LayerNormalization

logger = setup_logging('transformer_model')

class TransformerModel(BaseModel):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.model = None
        self.sequence_length = 10  # Длина последовательности для Transformer

    def _prepare_data(self, X: list, y: list = None) -> tuple:
        """Prepare sequential data for Transformer training or prediction."""
        X_seq, y_seq = [], []
        for i in range(len(X) - self.sequence_length):
            X_seq.append(X[i:i + self.sequence_length])
            if y is not None:
                y_seq.append(y[i + self.sequence_length])
        
        X_seq = np.array(X_seq)
        if y is not None:
            y_seq = np.array(y_seq)
            return X_seq, y_seq
        return X_seq

    def train(self, X: list, y: list) -> None:
        """Train the Transformer model with the given data."""
        try:
            # Подготавливаем данные для Transformer
            X_seq, y_seq = self._prepare_data(X, y)
            if len(X_seq) == 0:
                raise ValueError("Not enough data for Transformer training")

            # Создаём модель
            self.model = Sequential([
                tf.keras.layers.Input(shape=(self.sequence_length, 1)),
                MultiHeadAttention(num_heads=2, key_dim=1),
                LayerNormalization(epsilon=1e-6),
                Dense(50, activation='relu'),
                Dropout(0.2),
                Dense(1)
            ])

            self.model.compile(optimizer='adam', loss='mse')

            # Преобразуем данные для Transformer
            X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], 1))
            
            # Обучаем модель
            self.model.fit(X_seq, y_seq, epochs=10, batch_size=32, verbose=0)
            logger.info("Transformer model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train Transformer model: {str(e)}")
            raise

    def predict(self, X: list) -> list:
        """Make predictions using the trained Transformer model."""
        try:
            if self.model is None:
                raise ValueError("Transformer model is not trained")

            # Подготавливаем данные для предсказания
            X_seq = self._prepare_data(X)
            if len(X_seq) == 0:
                raise ValueError("Not enough data for Transformer prediction")

            X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], 1))
            
            # Делаем предсказания
            predictions = self.model.predict(X_seq, verbose=0)
            return predictions.flatten().tolist()
        except Exception as e:
            logger.error(f"Failed to make Transformer predictions: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    model = TransformerModel(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(model.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        # Получаем данные для обучения
        klines = model.market_data.get_klines(symbols[0], '1h', 50, 'binance')
        X = [kline['close'] for kline in klines[:-1]]  # Цены закрытия для обучения
        y = [kline['close'] for kline in klines[1:]]   # Следующие цены закрытия как целевые значения
        
        model.train(X, y)
        predictions = model.predict(X)
        print(f"Transformer Predictions for {symbols[0]}: {predictions}")
    else:
        print("No symbols available for testing")
