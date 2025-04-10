import random
from typing import List, Dict
from strategies import Strategy
from backtest_cycle import run_backtest

class GeneticOptimizer:
    def __init__(self, population_size: int, generations: int):
        self.population_size = population_size
        self.generations = generations

    def optimize(self, strategy: Strategy, data: Dict) -> Dict:
        """Optimize strategy parameters using a genetic algorithm."""
        population = self._initialize_population()
        for generation in range(self.generations):
            population = self._evolve_population(population, strategy, data)
            print(f"Generation {generation + 1}/{self.generations} completed")
        return self._get_best_individual(population, strategy, data)

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

    def _evaluate_individual(self, individual: Dict, strategy: Strategy, data: Dict) -> float:
        """Evaluate an individual by running a backtest."""
        strategy.params = individual
        result = run_backtest(strategy, data)
        return result["profit"]

    def _evolve_population(self, population: List[Dict], strategy: Strategy, data: Dict) -> List[Dict]:
        """Evolve the population: selection, crossover, mutation."""
        # Evaluate fitness of each individual
        fitness_scores = [(individual, self._evaluate_individual(individual, strategy, data)) for individual in population]
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

    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Perform crossover between two parents."""
        child = {}
        for key in parent1:
            child[key] = random.choice([parent1[key], parent2[key]])
        return child

    def _mutate(self, individual: Dict) -> Dict:
        """Mutate an individual."""
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

    def _get_best_individual(self, population: List[Dict], strategy: Strategy, data: Dict) -> Dict:
        """Get the best individual based on fitness."""
        fitness_scores = [(individual, self._evaluate_individual(individual, strategy, data)) for individual in population]
        best_individual, best_fitness = max(fitness_scores, key=lambda x: x[1])
        print(f"Best fitness: {best_fitness}")
        return best_individual
