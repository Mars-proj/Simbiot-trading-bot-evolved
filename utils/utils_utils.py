from trading_bot.logging_setup import setup_logging

logger = setup_logging('utils_utils')

def safe_div(a: float, b: float, default: float = 0.0) -> float:
    """Safely divide two numbers, return default if division by zero."""
    try:
        return a / b if b != 0 else default
    except Exception as e:
        logger.error(f"Failed to perform safe division: {str(e)}")
        return default

def calculate_dynamic_threshold(market_state: dict, base_value: float) -> float:
    """Calculate a dynamic threshold based on market state."""
    try:
        volatility = market_state['volatility']
        # Увеличиваем порог при высокой волатильности
        threshold = base_value * (1 + volatility)
        logger.debug(f"Calculated dynamic threshold: {threshold} (base: {base_value}, volatility: {volatility})")
        return threshold
    except Exception as e:
        logger.error(f"Failed to calculate dynamic threshold: {str(e)}")
        raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    threshold = calculate_dynamic_threshold(market_state, 10.0)
    print(f"Dynamic threshold: {threshold}")
    result = safe_div(10, 0)
    print(f"Safe division result: {result}")
