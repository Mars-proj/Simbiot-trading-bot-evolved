from trading_bot.logging_setup import setup_logging

logger = setup_logging('data_utils')

def normalize_klines(klines: list) -> list:
    """Normalize kline data to a standard format."""
    try:
        normalized = []
        for kline in klines:
            normalized.append({
                "timestamp": kline[0],
                "open": float(kline[1]),
                "high": float(kline[2]),
                "low": float(kline[3]),
                "close": float(kline[4]),
                "volume": float(kline[5])
            })
        logger.info(f"Normalized {len(normalized)} klines")
        return normalized
    except Exception as e:
        logger.error(f"Failed to normalize klines: {str(e)}")
        raise

def calculate_volatility(klines: list) -> float:
    """Calculate volatility based on kline data."""
    try:
        if not klines:
            return 0.0
        closes = [kline['close'] for kline in klines]
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        volatility = sum(returns) / len(returns) if returns else 0.0
        logger.info(f"Calculated volatility: {volatility}")
        return volatility
    except Exception as e:
        logger.error(f"Failed to calculate volatility: {str(e)}")
        raise

if __name__ == "__main__":
    # Test run
    klines = [
        [1625097600, "50000", "51000", "49000", "50500", "1000"],
        [1625097601, "50500", "52000", "50000", "51500", "1200"]
    ]
    normalized = normalize_klines(klines)
    volatility = calculate_volatility(normalized)
    print(f"Normalized klines: {normalized}")
    print(f"Volatility: {volatility}")
