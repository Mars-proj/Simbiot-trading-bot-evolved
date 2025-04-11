from trading_bot.logging_setup import setup_logging

logger = setup_logging('sentiment_analyzer')

class SentimentAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def analyze_sentiment(self, texts: list) -> float:
        """Analyze sentiment of texts (simplified)."""
        try:
            if not texts:
                logger.warning("No texts provided for sentiment analysis")
                return 0.0

            # Упрощённый анализ: считаем количество позитивных и негативных слов
            positive_words = ['good', 'great', 'bullish', 'up']
            negative_words = ['bad', 'poor', 'bearish', 'down']
            
            positive_count = sum(text.lower().count(word) for text in texts for word in positive_words)
            negative_count = sum(text.lower().count(word) for text in texts for word in negative_words)
            
            # Корректировка на основе волатильности
            sentiment_score = (positive_count - negative_count) / (positive_count + negative_count + 1)
            adjusted_score = sentiment_score * (1 - self.volatility / 2)
            
            logger.info(f"Sentiment score: {adjusted_score}")
            return adjusted_score
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = SentimentAnalyzer(market_state)
    texts = ["Market is going up, great news!", "Bearish trend, bad day"]
    score = analyzer.analyze_sentiment(texts)
    print(f"Sentiment score: {score}")
