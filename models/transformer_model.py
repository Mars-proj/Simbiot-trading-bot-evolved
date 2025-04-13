import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout, LayerNormalization, MultiHeadAttention

class TransformerModel:
    def __init__(self):
        self.model = tf.keras.Sequential([
            MultiHeadAttention(num_heads=2, key_dim=2),
            Dropout(0.1),
            LayerNormalization(epsilon=1e-6),
            Dense(64, activation='relu'),
            Dense(1, activation='sigmoid')
        ])

    def train(self, X_train, y_train):
        """Train the transformer model."""
        self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.model.fit(X_train, y_train, epochs=5, batch_size=32, validation_split=0.2)

    def predict(self, X_test):
        """Make predictions using the transformer model."""
        return self.model.predict(X_test)
