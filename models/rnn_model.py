from trading_bot.logging_setup import setup_logging
from .base_model import BaseModel
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense

logger = setup_logging('rnn_model')

class RNNModel(BaseModel):
    def __init__(self, market_state: dict, units: int = 50):
        super().__init__(market_state)
        self.units = units
        self.model = self._build_model()

    def _build_model(self):
        """Build the RNN model."""
        try:
            model = Sequential()
            model.add(SimpleRNN(units=self.units, return_sequences=True, input_shape=(None, 1)))
            model.add(SimpleRNN(units=self.units))
            model.add(Dense(1))
            model.compile(optimizer='adam', loss='mean_squared_error')
            logger.info("RNN model built successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to build RNN model: {str(e)}")
            raise

    def train(self, X, y, epochs: int = 10, batch_size: int = 32):
        """Train the RNN model."""
        try:
            # Корректируем данные на основе волатильности
            X_adjusted = self.adjust_data(X)
            y_adjusted = self.adjust_data(y)
            
            # Преобразуем данные для RNN (добавляем временное измерение)
            X_adjusted = np.reshape(X_adjusted, (X_adjusted.shape[0], X_adjusted.shape[1], 1))
            
            self.model.fit(X_adjusted, y_adjusted, epochs=epochs, batch_size=batch_size, verbose=0)
            logger.info("RNN model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train RNN model: {str(e)}")
            raise

    def predict(self, X):
        """Make predictions using the RNN model."""
        try:
            # Корректируем данные на основе волатильности
            X_adjusted = self.adjust_data(X)
            
            # Преобразуем данные для RNN
            X_adjusted = np.reshape(X_adjusted, (X_adjusted.shape[0], X_adjusted.shape[1], 1))
            
            predictions = self.model.predict(X_adjusted, verbose=0)
            logger.info(f"Made {len(predictions)} predictions with RNN model")
            return predictions
        except Exception as e:
            logger.error(f"Failed to make predictions with RNN model: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    model = RNNModel(market_state)
    X = np.array([[50000 + i * 100] for i in range(10)])
    y = np.array([51000 + i * 100 for i in range(10)])
    model.train(X, y)
    predictions = model.predict(X)
    print(f"Predictions: {predictions}")
