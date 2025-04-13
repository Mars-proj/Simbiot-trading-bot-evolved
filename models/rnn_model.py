import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
import tensorflow as tf

logger = setup_logging('rnn_model')

class RNNModel:
    def __init__(self):
        self.model = tf.keras.Sequential([
            tf.keras.layers.SimpleRNN(50, return_sequences=True, input_shape=(10, 1)),
            tf.keras.layers.SimpleRNN(50),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    def update(self, features: list, labels: list):
        """Update the model with new data."""
        try:
            self.model.fit(features, labels, epochs=1, verbose=0)
            logger.info("RNN model updated successfully")
        except Exception as e:
            logger.error(f"Failed to update RNN model: {str(e)}")
            raise
