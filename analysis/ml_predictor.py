import pandas as pd
import pickle
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from logging_setup import setup_logging

logger = setup_logging('ml_predictor')

class MLPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.training_data = {}

    def load_model(self, model_id: int):
        """Load a pre-trained ML model."""
        model_path = f"models/model_{model_id}.pkl"
        if not os.path.exists(model_path):
            logger.warning(f"Model file {model_path} not found, training new model")
            self.train_model(model_id)
        with open(model_path, 'rb') as f:
            self.models[model_id] = pickle.load(f)

    def train_model(self, model_id: int):
        """Train a new ML model if training data is available."""
        try:
            if model_id not in self.training_data:
                logger.error(f"No training data available for model {model_id}")
                raise ValueError(f"No training data available for model {model_id}")

            data = self.training_data[model_id]
            X = data[['returns', 'log_returns', 'rsi_14', 'sma_20', 'sma_50', 'bb_upper', 'bb_lower', 'macd', 'macd_signal']]
            y = data['price'].shift(-1)[:-1]  # Predict next price
            X = X[:-1]

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_scaled, y)

            # Save model and scaler
            model_path = f"models/model_{model_id}.pkl"
            os.makedirs("models", exist_ok=True)
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)

            self.models[model_id] = model
            self.scalers[model_id] = scaler
            logger.info(f"Trained and saved model {model_id}")
        except Exception as e:
            logger.error(f"Failed to train model {model_id}: {str(e)}")
            raise

    def update_training_data(self, model_id: int, data: pd.DataFrame):
        """Update training data for online learning."""
        try:
            if model_id not in self.training_data:
                self.training_data[model_id] = data
            else:
                self.training_data[model_id] = pd.concat([self.training_data[model_id], data], ignore_index=True)
                # Limit training data size to avoid memory issues
                if len(self.training_data[model_id]) > 10000:
                    self.training_data[model_id] = self.training_data[model_id].tail(10000)
            logger.info(f"Updated training data for model {model_id}")
        except Exception as e:
            logger.error(f"Failed to update training data for model {model_id}: {str(e)}")
            raise

    def predict(self, data: pd.DataFrame, model_id: int) -> float:
        """Predict the next price using a pre-trained ML model."""
        try:
            # Load model if not already loaded
            if model_id not in self.models:
                self.load_model(model_id)

            # Prepare features
            features = data[['returns', 'log_returns', 'rsi_14', 'sma_20', 'sma_50', 'bb_upper', 'bb_lower', 'macd', 'macd_signal']].tail(1)
            if features.empty:
                logger.error("No features available for prediction")
                raise ValueError("No features available for prediction")

            # Scale features using cached scaler
            scaled_features = self.scalers[model_id].transform(features)

            # Predict
            prediction = self.models[model_id].predict(scaled_features)[0]
            logger.info(f"Predicted price: {prediction}")

            # Update training data for online learning
            self.update_training_data(model_id, data)

            # Retrain model periodically (e.g., every 100 predictions)
            if len(self.training_data[model_id]) % 100 == 0:
                self.train_model(model_id)

            return prediction
        except Exception as e:
            logger.error(f"Failed to predict price: {str(e)}")
            raise

# Singleton instance
predictor = MLPredictor()

def predict(data: pd.DataFrame, model_id: int) -> float:
    """Wrapper for predictor.predict."""
    return predictor.predict(data, model_id)
