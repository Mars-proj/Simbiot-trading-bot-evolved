from trading_bot.logging_setup import setup_logging
from dotenv import load_dotenv
import os
from newsapi import NewsApiClient
import asyncio

# Загружаем переменные из .env
load_dotenv()

logger = setup_logging('news_fetcher')

class NewsFetcher:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.api_key = os.getenv('NEWSAPI_KEY', 'your_newsapi_key')
        self.newsapi = NewsApiClient(api_key=self.api_key)

    async def fetch_news(self, query: str, language: str = 'en', page_size: int = 10) -> list:
        """Fetch news articles related to the query asynchronously."""
        try:
            # Асинхронный запрос к NewsAPI
            loop = asyncio.get_event_loop()
            articles = await loop.run_in_executor(None, lambda: self.newsapi.get_everything(
                q=query,
                language=language,
                page_size=page_size,
                sort_by='relevancy'
            ))

            news = [
                {
                    'title': article['title'],
                    'description': article['description'],
                    'published_at': article['publishedAt'],
                    'source': article['source']['name']
                }
                for article in articles['articles']
            ]

            logger.info(f"Fetched {len(news)} news articles for query: {query}")
            return news
        except Exception as e:
            logger.error(f"Failed to fetch news for query {query}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    fetcher = NewsFetcher(market_state)
    
    async def main():
        news = await fetcher.fetch_news("Bitcoin")
        print(f"News articles: {news}")

    asyncio.run(main())
