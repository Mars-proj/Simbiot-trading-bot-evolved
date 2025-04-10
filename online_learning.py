import pandas as pd
import joblib

def update_model(data: pd.DataFrame, model_id: int) -> None:
    """Update the ML model with new data."""
    # Load existing model
    model_path = f"models/model_{model_id}.joblib"
    model = joblib.load(model_path)

    # Prepare features and target
    X = data[['sma_20', 'rsi', 'price_change', 'volatility']]
    y = data['price'].shift(-1)
    X = X[:-1]
    y = y[:-1]

    # Update model with new data
    model.fit(X, y)  # Incremental learning (RandomForest supports partial_fit indirectly)

    # Save updated model
    joblib.dump(model, model_path)
    print(f"Model {model_id} updated with new data")
