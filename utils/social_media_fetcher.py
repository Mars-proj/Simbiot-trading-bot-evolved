import tweepy
from trading_bot.logging_setup import setup_logging
from dotenv import load_dotenv
import os
import asyncio
from textblob import TextBlob

# Загружаем переменные из .env
load_dotenv()

logger = setup_logging('social_media_fetcher')

class SocialMediaFetcher:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', 'your_twitter_bearer_token')
        self.client = tweepy.Client(bearer_token=self.bearer_token)

    async def fetch_tweets(self, query: str, max_results: int = 10) -> list:
        """Fetch tweets related to the query asynchronously and analyze sentiment."""
        try:
            # Асинхронный запрос к Twitter API
            loop = asyncio.get_event_loop()
            tweets = await loop.run_in_executor(None, lambda: self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'lang']
            ))

            if not tweets.data:
                logger.info(f"No tweets found for query: {query}")
                return []

            # Анализируем настроения твитов
            tweet_data = []
            for tweet in tweets.data:
                if tweet.lang == 'en':  # Обрабатываем только твиты на английском
                    analysis = TextBlob(tweet.text)
                    sentiment = 'positive' if analysis.sentiment.polarity > 0 else 'negative' if analysis.sentiment.polarity < 0 else 'neutral'
                    tweet_data.append({
                        'text': tweet.text,
                        'created_at': str(tweet.created_at),
                        'sentiment': sentiment,
                        'polarity': analysis.sentiment.polarity
                    })

            logger.info(f"Fetched {len(tweet_data)} tweets for query: {query}")
            return tweet_data
        except Exception as e:
            logger.error(f"Failed to fetch tweets for query {query}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    fetcher = SocialMediaFetcher(market_state)
    
    async def main():
        tweets = await fetcher.fetch_tweets("Bitcoin")
        print(f"Tweets: {tweets}")

    asyncio.run(main())
