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
        if not all([api_key, api_secret, access_token, access_token_secret]):
            logger.error("Twitter API keys not found in .env file")
            raise ValueError("Twitter API keys not found")
        self.auth = tweepy.OAuthHandler(api_key, api_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth)
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def fetch_tweets(self, query: str, count: int = 10) -> list:
        """Fetch tweets based on a query."""
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
