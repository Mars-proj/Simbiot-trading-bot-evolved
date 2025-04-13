import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from newsapi import NewsApiClient
from utils.logging_setup import setup_logging
from dotenv import load_dotenv
from transformers import pipeline

logger = setup_logging('news_fetcher')

class NewsFetcher:
    def __init__(self, market_state: dict = None):
        self.market_state = market_state
        load_dotenv()
        api_key = os.getenv('NEWSAPI_KEY')
        if not api_key:
            logger.error("News API key not found in .env file")
            raise ValueError("News API key not found")
        self.client = NewsApiClient(api_key=api_key)
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def fetch_news(self, query: str, language: str = 'en', page_size: int = 10) -> list:
        """Fetch news articles based on a query."""
        try:
            logger.info(f"Fetching news for query: {query}")
            articles = self.client.get_everything(q=query, language=language, page_size=page_size)
            logger.info(f"Fetched {len(articles['articles'])} news articles for query: {query}")
            return articles['articles']
        except Exception as e:
            logger.error(f"Failed to fetch news: {str(e)}")
            return []

    def analyze_sentiment(self, text: str) -> float:
        """Analyze the sentiment of a given text using BERT."""
        try:
            result = self.sentiment_analyzer(text)[0]
            score = result['score'] if result['label'] == 'POSITIVE' else -result['score']
            return score
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            return 0.0

if __name__ == "__main__":
    # Test run
    fetcher = NewsFetcher()
    articles = fetcher.fetch_news("bitcoin")
    print(f"Fetched {len(articles)} articles")
