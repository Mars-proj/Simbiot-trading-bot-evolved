import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Dropout, LayerNormalization, MultiHeadAttention, GlobalAveragePooling1D
from tensorflow.keras.models import Model
from utils.logging_setup import setup_logging

logger = setup_logging('transformer_model')

# Отключаем использование GPU до установки CUDA 12.2 и CuDNN 9.3.0
os.environ["CUDA_VISIBLE_DEVICES"] = ""

class TransformerModel:
    def __init__(self, lookback=20, num_heads=4, d_model=128, dropout_rate=0.1):
        """Initialize the Transformer model."""
        self.lookback = lookback
        self.num_heads = num_heads
        self.d_model = d_model
        self.dropout_rate = dropout_rate
        self.model = self._build_model()

    def _build_model(self):
        """Build the Transformer model architecture."""
        try:
            inputs = Input(shape=(self.lookback, 1))
            x = Dense(self.d_model)(inputs)
            x = MultiHeadAttention(num_heads=self.num_heads, key_dim=self.d_model // self.num_heads)(x, x)
            x = Dropout(self.dropout_rate)(x)
            x = LayerNormalization(epsilon=1e-6)(x)
            x = GlobalAveragePooling1D()(x)
            x = Dense(64, activation='relu')(x)
            outputs = Dense(1, activation='linear')(x)
            model = Model(inputs, outputs)
            model.compile(optimizer='adam', loss='mse')
            logger.info("Transformer model built successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to build Transformer model: {str(e)}")
            raise

    def preprocess_data(self, klines):
        """Preprocess klines data for Transformer."""
        try:
            if len(klines) < self.lookback:
                logger.warning("Not enough klines data for Transformer preprocessing")
                return None, None

            prices = np.array([kline[4] for kline in klines])  # Use closing prices
            X, y = [], []
            for i in range(len(prices) - self.lookback):
                X.append(prices[i:i + self.lookback])
                y.append(prices[i + self.lookback])
            X = np.array(X).reshape(-1, self.lookback, 1)
            y = np.array(y)
            logger.info(f"Preprocessed {len(X)} samples for Transformer")
            return X, y
        except Exception as e:
            logger.error(f"Failed to preprocess data for Transformer: {str(e)}")
            return None, None

    def train(self, klines, epochs=10, batch_size=32):
        """Train the Transformer model."""
        try:
            X, y = self.preprocess_data(klines)
            if X is None or y is None:
                return False
            self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
            logger.info("Transformer model trained successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to train Transformer model: {str(e)}")
            return False

    def predict(self, klines):
        """Predict the next price using the Transformer model."""
        try:
            X, _ = self.preprocess_data(klines)
            if X is None:
                return None
            prediction = self.model.predict(X[-1].reshape(1, self.lookback, 1), verbose=0)
            logger.info(f"Transformer prediction: {prediction[0][0]}")
            return prediction[0][0]
        except Exception as e:
            logger.error(f"Failed to predict with Transformer model: {str(e)}")
            return None
