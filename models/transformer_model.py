import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from utils.logging_setup import setup_logging

logger = setup_logging('transformer_model')

class TransformerModel:
    def __init__(self):
        self.model = None  # Инициализируем model как None, будем создавать его при вызове train

    def build_model(self, input_shape):
        """Build a new Keras Sequential model."""
        model = Sequential([
            Dense(64, activation='relu', input_shape=(input_shape[1],)),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='sigmoid')
        ])
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def train(self, X: np.ndarray, y: np.ndarray):
        """Train the transformer model with the given data."""
        try:
            # Создаём новую модель при каждом вызове train
            self.model = self.build_model(X.shape)
            self.model.fit(X, y, epochs=5, batch_size=32, verbose=0)
            logger.info("Transformer model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train transformer model: {str(e)}")
            raise

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict using the transformer model."""
        try:
            if self.model is None:
                raise ValueError("Model has not been trained yet")
            predictions = self.model.predict(X, verbose=0)
            return predictions.flatten()
        except Exception as e:
            logger.error(f"Failed to predict with transformer model: {str(e)}")
            raise
