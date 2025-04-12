import random
from typing import List, Dict
from trading_bot.strategies.strategy import Strategy
from trading_bot.logging_setup import setup_logging

logger = setup_logging('genetic_optimizer')

class GeneticOptimizer:
    def __init__(self, market_state: dict, population_size: int, generations: int):
        self.volatility = market_state['volatility']
        self.population_size = population_size
        self.generations = generations

    def optimize(self, strategy: Strategy, symbols: list, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> Dict:
        """Optimize strategy parameters using a genetic algorithm."""
        try:
            population = self._initialize_population()
            for generation in range(self.generations):
                population = self._evolve_population(population, strategy, symbols, timeframe, limit, exchange_name)
                logger.info(f"Generation {generation + 1}/{self.generations} completed")
            best_individual = self._get_best_individual(population, strategy, symbols, timeframe, limit, exchange_name)
            logger.info(f"Optimization completed with best individual: {best_individual}")
            return best_individual
        except Exception as e:
            logger.error(f"Failed to optimize strategy: {str(e)}")
            raise

    def _initialize_population(self) -> List[Dict]:
        """Initialize a population of individuals with random parameters."""
        population = []
        for _ in range(self.population_size):
            individual = {
                "threshold": random.uniform(5000, 15000),  # Price threshold for signals
                "stop_loss": random.uniform(0.01, 0.05),  # Stop-loss percentage
                "take_profit": random.uniform(0.02, 0.10)  # Take-profit percentage
            }
            population.append(individual)
        return population

    def _evaluate_individual(self, individual: Dict, strategy: Strategy, symbols: list, timeframe: str, limit: int, exchange_name: str) -> float:
        """Evaluate an individual by running a backtest."""
        try:
            strategy.params = individual
            result = strategy.backtest(symbols, timeframe, limit, exchange_name)
            total_profit = sum(r['profit'] for r in result.values())
            return total_profit
        except Exception as e:
            logger.error(f"Failed to evaluate individual: {str(e)}")
            raise

    def _evolve_population(self, population: List[Dict], strategy: Strategy, symbols: list, timeframe: str, limit: int, exchange_name: str) -> List[Dict]:
        """Evolve the population: selection, crossover, mutation."""
        try:
            # Evaluate fitness of each individual
            fitness_scores = [(individual, self._evaluate_individual(individual, strategy, symbols, timeframe, limit, exchange_name)) for individual in population]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)  # Sort by profit (descending)

            # Select top 50% for reproduction
            elite_size = self.population_size // 2
            elite = [individual for individual, _ in fitness_scores[:elite_size]]

            # Create new population through crossover and mutation
            new_population = elite.copy()
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(elite, 2)
                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_population.append(child)

            return new_population[:self.population_size]
        except Exception as e:
            logger.error(f"Failed to evolve population: {str(e)}")
            raise

    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Perform crossover between two parents."""
        try:
            child = {}
            for key in parent1:
                child[key] = random.choice([parent1[key], parent2[key]])
            return child
        except Exception as e:
            logger.error(f"Failed to perform crossover: {str(e)}")
            raise

    def _mutate(self, individual: Dict) -> Dict:
        """Mutate an individual."""
        try:
            mutation_rate = 0.1
            mutated = individual.copy()
            for key in mutated:
                if random.random() < mutation_rate:
                    if key == "threshold":
                        mutated[key] = random.uniform(5000, 15000)
                    elif key == "stop_loss":
                        mutated[key] = random.uniform(0.01, 0.05)
                    elif key == "take_profit":
                        mutated[key] = random.uniform(0.02, 0.10)
            return mutated
        except Exception as e:
            logger.error(f"Failed to mutate individual: {str(e)}")
            raise

    def _get_best_individual(self, population: List[Dict], strategy: Strategy, symbols: list, timeframe: str, limit: int, exchange_name: str) -> Dict:
        """Get the best individual based on fitness."""
        try:
            fitness_scores = [(individual, self._evaluate_individual(individual, strategy, symbols, timeframe, limit, exchange_name)) for individual in population]
            best_individual, best_fitness = max(fitness_scores, key=lambda x: x[1])
            logger.info(f"Best fitness: {best_fitness}")
            return best_individual
        except Exception as e:
            logger.error(f"Failed to get best individual: {str(e)}")
            raise
