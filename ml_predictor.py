import pandas as pd
import joblib

def predict(data: pd.DataFrame, model_id: int) -> float:
    """Make a prediction using an ML model."""
    # Load model
    model_path = f"models/model_{model_id}.joblib"
    model = joblib.load(model_path)

    # Prepare features
    X = data[['sma_20', 'rsi', 'price_change', 'volatility']]
    X = X.iloc[-1:]  # Use the last row for prediction

    # Predict
    prediction = model.predict(X)[0]
    return float(prediction)
