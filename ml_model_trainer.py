import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

def train_model(model_id: int, data: pd.DataFrame) -> None:
    """Train an ML model and save it."""
    # Prepare features and target
    X = data[['sma_20', 'rsi', 'price_change', 'volatility']]
    y = data['price'].shift(-1)  # Predict next price
    X = X[:-1]  # Remove last row (no target for it)
    y = y[:-1]

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save model
    model_path = f"models/model_{model_id}.joblib"
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Model {model_id} trained and saved to {model_path}")
