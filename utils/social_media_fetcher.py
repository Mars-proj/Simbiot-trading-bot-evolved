import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tweepy
from utils.logging_setup import setup_logging
from dotenv import load_dotenv
from transformers import pipeline

logger = setup_logging('social_media_fetcher')

class SocialMediaFetcher:
    def __init__(self, market_state: dict = None):
        self.market_state = market_state
        load_dotenv()
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Проверяем наличие всех ключей
        if not all([api_key, api_secret, access_token, access_token_secret]):
            logger.warning("Twitter API keys not found in .env file. Social media fetching will be disabled.")
            self.api = None
        else:
            try:
                self.auth = tweepy.OAuthHandler(api_key, api_secret)
                self.auth.set_access_token(access_token, access_token_secret)
                self.api = tweepy.API(self.auth)
                logger.info("Twitter API initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize Twitter API: {str(e)}. Social media fetching will be disabled.")
                self.api = None
        
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english") if self.api else None

    def fetch_tweets(self, query: str, count: int = 10) -> list:
        """Fetch tweets based on a query."""
        if self.api is None:
            logger.warning("Twitter API not initialized. Returning empty tweet list.")
            return []
        
        try:
            logger.info(f"Fetching tweets for query: {query}")
            tweets = self.api.search_tweets(q=query, count=count, lang='en', tweet_mode='extended')
            tweet_texts = [tweet.full_text for tweet in tweets]
            logger.info(f"Fetched {len(tweet_texts)} tweets for query: {query}")
            return tweet_texts
        except Exception as e:
            logger.error(f"Failed to fetch tweets: {str(e)}")
            return []

    def analyze_sentiment(self, text: str) -> float:
        """Analyze the sentiment of a given text using BERT."""
        if self.sentiment_analyzer is None:
            logger.warning("Sentiment analyzer not initialized due to missing Twitter API. Returning neutral sentiment.")
            return 0.0
        
        try:
            result = self.sentiment_analyzer(text)[0]
            score = result['score'] if result['label'] == 'POSITIVE' else -result['score']
            return score
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            return 0.0

if __name__ == "__main__":
    # Test run
    fetcher = SocialMediaFetcher()
    tweets = fetcher.fetch_tweets("bitcoin")
    print(f"Fetched {len(tweets)} tweets")
