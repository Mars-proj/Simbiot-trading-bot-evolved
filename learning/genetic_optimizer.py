from trading_bot.logging_setup import setup_logging
import numpy as np
import random

logger = setup_logging('genetic_optimizer')

class GeneticOptimizer:
    def __init__(self, market_state: dict, population_size: int = 50, generations: int = 20):
        self.volatility = market_state['volatility']
        self.population_size = population_size
        self.generations = generations

    def optimize(self, strategy_params: dict, fitness_function) -> dict:
        """Optimize strategy parameters using a genetic algorithm."""
        try:
            # Инициализируем популяцию
            population = [self._generate_individual(strategy_params) for _ in range(self.population_size)]
            
            for generation in range(self.generations):
                # Оцениваем фитнес каждого индивида
                fitness_scores = [fitness_function(individual) for individual in population]
                
                # Выбираем лучших индивидов
                selected = self._select(population, fitness_scores)
                
                # Выполняем скрещивание и мутацию
                offspring = []
                for i in range(0, len(selected), 2):
                    if i + 1 < len(selected):
                        child1, child2 = self._crossover(selected[i], selected[i + 1])
                        offspring.append(self._mutate(child1))
                        offspring.append(self._mutate(child2))
                
                # Обновляем популяцию
                population = offspring + selected[:self.population_size - len(offspring)]
            
            # Возвращаем лучшего индивида
            fitness_scores = [fitness_function(individual) for individual in population]
            best_individual = population[np.argmax(fitness_scores)]
            logger.info(f"Best parameters after optimization: {best_individual}")
            return best_individual
        except Exception as e:
            logger.error(f"Failed to optimize parameters: {str(e)}")
            raise

    def _generate_individual(self, strategy_params):
        """Generate a random individual based on parameter ranges."""
        individual = {}
        for param, (min_val, max_val) in strategy_params.items():
            if isinstance(min_val, int) and isinstance(max_val, int):
                individual[param] = random.randint(min_val, max_val)
            else:
                individual[param] = random.uniform(min_val, max_val)
        return individual

    def _select(self, population, fitness_scores):
        """Select individuals for the next generation."""
        sorted_indices = np.argsort(fitness_scores)[::-1]
        return [population[i] for i in sorted_indices[:self.population_size // 2]]

    def _crossover(self, parent1, parent2):
        """Perform crossover between two parents."""
        child1, child2 = {}, {}
        for key in parent1:
            if random.random() < 0.5:
                child1[key] = parent1[key]
                child2[key] = parent2[key]
            else:
                child1[key] = parent2[key]
                child2[key] = parent1[key]
        return child1, child2

    def _mutate(self, individual):
        """Mutate an individual."""
        mutated = individual.copy()
        for key in mutated:
            if random.random() < 0.1:  # 10% шанс мутации
                if isinstance(mutated[key], int):
                    mutated[key] += random.randint(-5, 5)
                else:
                    mutated[key] += random.uniform(-0.1, 0.1) * (1 + self.volatility)
        return mutated

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    optimizer = GeneticOptimizer(market_state)
    strategy_params = {
        'period': (10, 30),
        'std_dev': (1.5, 2.5)
    }
    def fitness_function(params):
        return random.uniform(0, 100)  # Пример функции фитнеса
    best_params = optimizer.optimize(strategy_params, fitness_function)
    print(f"Best parameters: {best_params}")
