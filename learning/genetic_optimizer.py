import random
from trading_bot.logging_setup import setup_logging
from trading_bot.strategies.strategy import Strategy
from trading_bot.data_sources.market_data import MarketData
from trading_bot.learning.backtester import Backtester

logger = setup_logging('genetic_optimizer')

class GeneticOptimizer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)
        self.backtester = Backtester(market_state)
        self.population_size = 50
        self.generations = 20
        self.mutation_rate = 0.1

    def generate_random_strategy(self) -> dict:
        """Generate a random trading strategy with parameters."""
        strategy_types = ['rsi', 'bollinger', 'macd']
        strategy_type = random.choice(strategy_types)

        if strategy_type == 'rsi':
            return {
                'type': 'rsi',
                'period': random.randint(10, 20),
                'overbought': random.uniform(60, 80),
                'oversold': random.uniform(20, 40)
            }
        elif strategy_type == 'bollinger':
            return {
                'type': 'bollinger',
                'period': random.randint(10, 30),
                'std_dev_multiplier': random.uniform(1.5, 3.0)
            }
        elif strategy_type == 'macd':
            return {
                'type': 'macd',
                'short_period': random.randint(5, 15),
                'long_period': random.randint(20, 30),
                'signal_period': random.randint(5, 15)
            }

    def crossover(self, parent1: dict, parent2: dict) -> dict:
        """Perform crossover between two strategies."""
        child = parent1.copy()
        for key in child:
            if random.random() < 0.5:
                child[key] = parent2[key]
        return child

    def mutate(self, strategy: dict) -> dict:
        """Mutate a strategy's parameters."""
        mutated = strategy.copy()
        if random.random() < self.mutation_rate:
            if mutated['type'] == 'rsi':
                mutated['period'] = random.randint(10, 20)
                mutated['overbought'] = random.uniform(60, 80)
                mutated['oversold'] = random.uniform(20, 40)
            elif mutated['type'] == 'bollinger':
                mutated['period'] = random.randint(10, 30)
                mutated['std_dev_multiplier'] = random.uniform(1.5, 3.0)
            elif mutated['type'] == 'macd':
                mutated['short_period'] = random.randint(5, 15)
                mutated['long_period'] = random.randint(20, 30)
                mutated['signal_period'] = random.randint(5, 15)
        return mutated

    async def optimize(self, symbols: list, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> dict:
        """Optimize trading strategies using a genetic algorithm."""
        try:
            # Инициализируем популяцию
            population = [self.generate_random_strategy() for _ in range(self.population_size)]
            
            for generation in range(self.generations):
                # Оцениваем каждую стратегию через бэктестинг
                fitness_scores = []
                for strategy in population:
                    # Создаём временную стратегию для бэктестинга
                    if strategy['type'] == 'rsi':
                        temp_strategy = RSIStrategy({'volatility': self.volatility})
                        temp_strategy.rsi_period = strategy['period']
                        temp_strategy.overbought_threshold = strategy['overbought']
                        temp_strategy.oversold_threshold = strategy['oversold']
                    elif strategy['type'] == 'bollinger':
                        temp_strategy = BollingerStrategy({'volatility': self.volatility})
                        temp_strategy.bollinger_period = strategy['period']
                        temp_strategy.std_dev_multiplier = strategy['std_dev_multiplier']
                    elif strategy['type'] == 'macd':
                        temp_strategy = MACDStrategy({'volatility': self.volatility})
                        temp_strategy.short_period = strategy['short_period']
                        temp_strategy.long_period = strategy['long_period']
                        temp_strategy.signal_period = strategy['signal_period']

                    # Запускаем бэктестинг
                    result = await self.backtester.run_backtest(symbols, temp_strategy, timeframe, limit, exchange_name)
                    total_profit = sum(res['profit'] for res in result.values())
                    fitness_scores.append((strategy, total_profit))

                # Сортируем по фитнесу (прибыли)
                fitness_scores.sort(key=lambda x: x[1], reverse=True)
                logger.info(f"Generation {generation + 1}: Best profit = {fitness_scores[0][1]}")

                # Выбираем лучших для следующего поколения
                next_population = [strategy for strategy, _ in fitness_scores[:self.population_size // 2]]

                # Создаём потомков через кроссовер и мутацию
                while len(next_population) < self.population_size:
                    parent1, parent2 = random.sample(next_population, 2)
                    child = self.crossover(parent1, parent2)
                    child = self.mutate(child)
                    next_population.append(child)

                population = next_population

            # Возвращаем лучшую стратегию
            best_strategy, best_profit = fitness_scores[0]
            logger.info(f"Best strategy after optimization: {best_strategy} with profit {best_profit}")
            return best_strategy
        except Exception as e:
            logger.error(f"Failed to optimize strategies: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    optimizer = GeneticOptimizer(market_state)
    
    async def main():
        symbols = ['BTC/USDT', 'ETH/USDT']
        best_strategy = await optimizer.optimize(symbols, '1h', 30, 'mexc')
        print(f"Best strategy: {best_strategy}")

    asyncio.run(main())
