from trading_bot.logging_setup import setup_logging
from .base_model import BaseModel
import numpy as np
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, MultiHeadAttention, LayerNormalization, Dropout

logger = setup_logging('transformer_model')

class TransformerModel(BaseModel):
    def __init__(self, market_state: dict, num_heads: int = 4, d_model: int = 64):
        super().__init__(market_state)
        self.num_heads = num_heads
        self.d_model = d_model
        self.model = self._build_model()

    def _build_model(self):
        """Build the Transformer model."""
        try:
            inputs = Input(shape=(None, 1))
            x = Dense(self.d_model)(inputs)
            x = MultiHeadAttention(num_heads=self.num_heads, key_dim=self.d_model)(x, x)
            x = Dropout(0.1)(x)
            x = LayerNormalization(epsilon=1e-6)(x)
            x = Dense(1)(x)
            model = Model(inputs=inputs, outputs=x)
            model.compile(optimizer='adam', loss='mean_squared_error')
            logger.info("Transformer model built successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to build Transformer model: {str(e)}")
            raise

    def train(self, X, y, epochs: int = 10, batch_size: int = 32):
        """Train the Transformer model."""
        try:
            # Корректируем данные на основе волатильности
            X_adjusted = self.adjust_data(X)
            y_adjusted = self.adjust_data(y)
            
            # Преобразуем данные для Transformer
            X_adjusted = np.reshape(X_adjusted, (X_adjusted.shape[0], X_adjusted.shape[1], 1))
            
            self.model.fit(X_adjusted, y_adjusted, epochs=epochs, batch_size=batch_size, verbose=0)
            logger.info("Transformer model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train Transformer model: {str(e)}")
            raise

    def predict(self, X):
        """Make predictions using the Transformer model."""
        try:
            # Корректируем данные на основе волатильности
            X_adjusted = self.adjust_data(X)
            
            # Преобразуем данные для Transformer
            X_adjusted = np.reshape(X_adjusted, (X_adjusted.shape[0], X_adjusted.shape[1], 1))
            
            predictions = self.model.predict(X_adjusted, verbose=0)
            logger.info(f"Made {len(predictions)} predictions with Transformer model")
            return predictions
        except Exception as e:
            logger.error(f"Failed to make predictions with Transformer model: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    model = TransformerModel(market_state)
    X = np.array([[50000 + i * 100] for i in range(10)])
    y = np.array([51000 + i * 100 for i in range(10)])
    model.train(X, y)
    predictions = model.predict(X)
    print(f"Predictions: {predictions}")
