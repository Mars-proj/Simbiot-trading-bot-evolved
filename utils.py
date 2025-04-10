# Default configuration from global_objects.py
DEFAULT_TIMEFRAME = "1h"
DEFAULT_SYMBOL = "BTC/USDT"

def safe_float(value: str) -> float:
    """Convert a string to float safely."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
