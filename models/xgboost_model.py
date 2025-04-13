import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
import xgboost as xgb

logger = setup_logging('xgboost_model')

class XGBoostModel:
    def __init__(self):
        self.model = xgb.XGBClassifier()

    def update(self, features: list, labels: list):
        """Update the model with new data."""
        try:
            self.model.fit(features, labels)
            logger.info("XGBoost model updated successfully")
        except Exception as e:
            logger.error(f"Failed to update XGBoost model: {str(e)}")
            raise
