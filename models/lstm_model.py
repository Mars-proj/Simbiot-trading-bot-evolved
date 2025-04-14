import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from utils.logging_setup import setup_logging

logger = setup_logging('lstm_model')

class LSTMModel:
    def __init__(self, lookback=20, units=128, dropout_rate=0.2):
        """Initialize the LSTM model."""
        self.lookback = lookback
        self.units = units
        self.dropout_rate = dropout_rate
        self.model = self._build_model()

    def _build_model(self):
        """Build the LSTM model architecture."""
        try:
            model = Sequential([
                LSTM(self.units, input_shape=(self.lookback, 1), return_sequences=True),
                Dropout(self.dropout_rate),
                LSTM(self.units // 2),
                Dropout(self.dropout_rate),
                Dense(1, activation='linear')
            ])
            model.compile(optimizer='adam', loss='mse')
            logger.info("LSTM model built successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to build LSTM model: {str(e)}")
            raise

    def preprocess_data(self, klines):
        """Preprocess klines data for LSTM."""
        try:
            if len(klines) < self.lookback:
                logger.warning("Not enough klines data for LSTM preprocessing")
                return None, None

            prices = np.array([kline[4] for kline in klines])  # Use closing prices
            X, y = [], []
            for i in range(len(prices) - self.lookback):
                X.append(prices[i:i + self.lookback])
                y.append(prices[i + self.lookback])
            X = np.array(X).reshape(-1, self.lookback, 1)
            y = np.array(y)
            logger.info(f"Preprocessed {len(X)} samples for LSTM")
            return X, y
        except Exception as e:
            logger.error(f"Failed to preprocess data for LSTM: {str(e)}")
            return None, None

    def train(self, klines, epochs=10, batch_size=32):
        """Train the LSTM model."""
        try:
            X, y = self.preprocess_data(klines)
            if X is None or y is None:
                return False
            self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
            logger.info("LSTM model trained successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to train LSTM model: {str(e)}")
            return False

    def predict(self, klines):
        """Predict the next price using the LSTM model."""
        try:
            X, _ = self.preprocess_data(klines)
            if X is None:
                return None
            prediction = self.model.predict(X[-1].reshape(1, self.lookback, 1), verbose=0)
            logger.info(f"LSTM prediction: {prediction[0][0]}")
            return prediction[0][0]
        except Exception as e:
            logger.error(f"Failed to predict with LSTM model: {str(e)}")
            return None
