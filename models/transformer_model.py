import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
import tensorflow as tf

logger = setup_logging('transformer_model')

class TransformerModel:
    def __init__(self):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(10, 1)),
            tf.keras.layers.MultiHeadAttention(num_heads=2, key_dim=2),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def update(self, features: list, labels: list):
        """Update the model with new data."""
        try:
            self.model.fit(features, labels, epochs=1, verbose=0)
            logger.info("Transformer model updated successfully")
        except Exception as e:
            logger.error(f"Failed to update Transformer model: {str(e)}")
            raise
