from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from .base_model import BaseModel
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense, Dropout

logger = setup_logging('rnn_model')

class RNNModel(BaseModel):
    def __init__(self, market_state: dict):
        super().__init__(market_state)
        self.model = None
        self.sequence_length = 10  # Длина последовательности для RNN

    def _prepare_data(self, X: list, y: list = None) -> tuple:
        """Prepare sequential data for RNN training or prediction."""
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
        """Train the RNN model with the given data."""
        try:
            # Подготавливаем данные для RNN
            X_seq, y_seq = self._prepare_data(X, y)
            if len(X_seq) == 0:
                raise ValueError("Not enough data for RNN training")

            # Создаём модель
            self.model = Sequential([
                SimpleRNN(50, activation='tanh', input_shape=(self.sequence_length, 1), return_sequences=True),
                Dropout(0.2),
                SimpleRNN(50, activation='tanh'),
                Dropout(0.2),
                Dense(1)
            ])

            self.model.compile(optimizer='adam', loss='mse')

            # Преобразуем данные для RNN
            X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], 1))
            
            # Обучаем модель
            self.model.fit(X_seq, y_seq, epochs=10, batch_size=32, verbose=0)
            logger.info("RNN model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train RNN model: {str(e)}")
            raise

    def predict(self, X: list) -> list:
        """Make predictions using the trained RNN model."""
        try:
            if self.model is None:
                raise ValueError("RNN model is not trained")

            # Подготавливаем данные для предсказания
            X_seq = self._prepare_data(X)
            if len(X_seq) == 0:
                raise ValueError("Not enough data for RNN prediction")

            X_seq = X_seq.reshape((X_seq.shape[0], X_seq.shape[1], 1))
            
            # Делаем предсказания
            predictions = self.model.predict(X_seq, verbose=0)
            return predictions.flatten().tolist()
        except Exception as e:
            logger.error(f"Failed to make RNN predictions: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    model = RNNModel(market_state)
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
        print(f"RNN Predictions for {symbols[0]}: {predictions}")
    else:
        print("No symbols available for testing")
