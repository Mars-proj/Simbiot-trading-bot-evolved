import numpy as np
from utils.logging_setup import setup_logging
import random

logger = setup_logging('strategy_evolution')

class StrategyEvolution:
    def __init__(self, market_data, volatility_analyzer, population_size=50, generations=10):
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.population_size = population_size
        self.generations = generations
        self.population = []
        self.indicators = ['rsi', 'macd', 'bollinger', 'mean_reversion', 'trend']
        self.best_strategy = None

    def initialize_population(self):
        """Создаём начальную популяцию стратегий с комбинациями индикаторов."""
        for _ in range(self.population_size):
            # Выбираем 1-2 индикатора для комбинации
            num_indicators = random.randint(1, 2)
            selected_indicators = random.sample(self.indicators, num_indicators)
            strategy = {
                'indicators': {},
                'weights': {}
            }

            # Инициализируем параметры для каждого индикатора
            for indicator in selected_indicators:
                if indicator == 'rsi':
                    strategy['indicators']['rsi'] = {
                        'period': random.randint(5, 20),
                        'overbought': random.uniform(60, 80),
                        'oversold': random.uniform(20, 40),
                        'adx_threshold': random.uniform(20, 30)
                    }
                elif indicator == 'macd':
                    strategy['indicators']['macd'] = {
                        'fast_period': random.randint(8, 16),
                        'slow_period': random.randint(20, 30),
                        'signal_period': random.randint(5, 12)
                    }
                elif indicator == 'bollinger':
                    strategy['indicators']['bollinger'] = {
                        'period': random.randint(10, 30),
                        'std_dev': random.uniform(1.5, 3.0)
                    }
                elif indicator == 'mean_reversion':
                    strategy['indicators']['mean_reversion'] = {
                        'lookback_period': random.randint(10, 30),
                        'z_score_threshold': random.uniform(1.5, 3.0)
                    }
                else:  # trend
                    strategy['indicators']['trend'] = {
                        'lookback_period': random.randint(20, 60)
                    }
                # Вес индикатора для принятия решения
                strategy['weights'][indicator] = random.uniform(0.3, 0.7)

            # Нормализуем веса, чтобы сумма была равна 1
            total_weight = sum(strategy['weights'].values())
            for indicator in strategy['weights']:
                strategy['weights'][indicator] /= total_weight

            self.population.append(strategy)
        logger.info(f"Initialized population with {self.population_size} strategies")

    def evaluate_strategy(self, strategy, klines):
        """Оцениваем производительность стратегии на основе симуляции."""
        try:
            closes = [kline[4] for kline in klines][-100:]
            if len(closes) < 40:
                return 0.0

            profit = 0.0
            position = 0  # 0 - нет позиции, 1 - лонг, -1 - шорт
            entry_price = 0.0

            # Рассчитываем сигналы для каждого индикатора
            signals = {}
            for indicator, params in strategy['indicators'].items():
                signal_score = 0.0
                if indicator == 'rsi':
                    period = params['period']
                    overbought = params['overbought']
                    oversold = params['oversold']
                    adx_threshold = params['adx_threshold']

                    deltas = np.diff(closes)
                    gains = np.where(deltas > 0, deltas, 0)
                    losses = np.where(deltas < 0, -deltas, 0)
                    avg_gain = np.mean(gains[:period]) if len(gains) >= period else 0
                    avg_loss = np.mean(losses[:period]) if len(losses) >= period else 0
                    for i in range(period, len(deltas)):
                        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
                    rs = avg_gain / avg_loss if avg_loss != 0 else 0
                    rsi = 100 - (100 / (1 + rs))

                    highs = [kline[2] for kline in klines][-period:]
                    lows = [kline[3] for kline in klines][-period:]
                    tr = [max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])) for i in range(1, len(highs))]
                    adx = np.mean(tr) if tr else 0

                    if rsi > overbought and adx > adx_threshold:
                        signal_score = -1.0  # Продать
                    elif rsi < oversold and adx > adx_threshold:
                        signal_score = 1.0  # Купить

                elif indicator == 'macd':
                    fast_period = params['fast_period']
                    slow_period = params['slow_period']
                    signal_period = params['signal_period']

                    def ema(data, period):
                        weights = np.exp(np.linspace(-1., 0., period))
                        weights /= weights.sum()
                        return np.convolve(data, weights, mode='valid')[0]

                    fast_ema = ema(np.array(closes[-fast_period:]), fast_period)
                    slow_ema = ema(np.array(closes[-slow_period:]), slow_period)
                    macd_line = fast_ema - slow_ema
                    signal_line = ema(np.array([fast_ema - slow_ema] * signal_period), signal_period)

                    if macd_line > signal_line:
                        signal_score = 1.0  # Купить
                    elif macd_line < signal_line:
                        signal_score = -1.0  # Продать

                elif indicator == 'bollinger':
                    period = params['period']
                    std_dev = params['std_dev']

                    lookback_data = closes[-period:]
                    sma = np.mean(lookback_data)
                    std = np.std(lookback_data)
                    upper_band = sma + std_dev * std
                    lower_band = sma - std_dev * std

                    if closes[-1] > upper_band:
                        signal_score = -1.0  # Продать
                    elif closes[-1] < lower_band:
                        signal_score = 1.0  # Купить

                elif indicator == 'mean_reversion':
                    lookback_period = params['lookback_period']
                    z_score_threshold = params['z_score_threshold']
                    lookback_data = closes[-lookback_period:]
                    mean = np.mean(lookback_data)
                    std = np.std(lookback_data)
                    z_score = (closes[-1] - mean) / std if std != 0 else 0

                    if z_score > z_score_threshold:
                        signal_score = -1.0  # Продать
                    elif z_score < -z_score_threshold:
                        signal_score = 1.0  # Купить

                else:  # trend
                    lookback_period = params['lookback_period']
                    short_ma = np.mean(closes[-10:])
                    long_ma = np.mean(closes[-lookback_period:])
                    if short_ma > long_ma:
                        signal_score = 1.0  # Купить
                    elif short_ma < long_ma:
                        signal_score = -1.0  # Продать

                signals[indicator] = signal_score

            # Комбинируем сигналы с учётом весов
            combined_signal = sum(signals[indicator] * strategy['weights'][indicator] for indicator in signals)
            if combined_signal > 0.5 and position != 1:
                if position == -1:
                    profit += (entry_price - closes[-1])
                position = 1
                entry_price = closes[-1]
            elif combined_signal < -0.5 and position != -1:
                if position == 1:
                    profit += (closes[-1] - entry_price)
                position = -1
                entry_price = closes[-1]

            return profit if profit > 0 else 0.0
        except Exception as e:
            logger.error(f"Failed to evaluate strategy: {str(e)}")
            return 0.0

    def evolve(self, klines):
        """Эволюция стратегий через генетический алгоритм."""
        try:
            self.initialize_population()

            for generation in range(self.generations):
                # Оценка популяции
                fitness_scores = []
                for strategy in self.population:
                    score = self.evaluate_strategy(strategy, klines)
                    fitness_scores.append((strategy, score))

                # Сортировка по производительности
                fitness_scores.sort(key=lambda x: x[1], reverse=True)
                self.best_strategy = fitness_scores[0][0]
                logger.info(f"Generation {generation}: Best fitness score = {fitness_scores[0][1]}")

                # Выбор лучших стратегий
                elite_size = self.population_size // 4
                new_population = [s[0] for s in fitness_scores[:elite_size]]

                # Скрещивание и мутация
                while len(new_population) < self.population_size:
                    parent1, parent2 = random.choices(fitness_scores[:self.population_size//2], k=2)
                    child = self.crossover(parent1[0], parent2[0])
                    child = self.mutate(child)
                    new_population.append(child)

                self.population = new_population

            return self.best_strategy
        except Exception as e:
            logger.error(f"Failed to evolve strategies: {str(e)}")
            return None

    def crossover(self, parent1, parent2):
        """Скрещивание двух стратегий."""
        child = {'indicators': {}, 'weights': {}}

        # Объединяем индикаторы из обоих родителей
        all_indicators = list(set(list(parent1['indicators'].keys()) + list(parent2['indicators'].keys())))
        num_indicators = random.randint(1, min(len(all_indicators), 2))
        selected_indicators = random.sample(all_indicators, num_indicators)

        for indicator in selected_indicators:
            if indicator in parent1['indicators'] and indicator in parent2['indicators']:
                # Если индикатор есть у обоих родителей, скрещиваем параметры
                parent1_params = parent1['indicators'][indicator]
                parent2_params = parent2['indicators'][indicator]
                child_params = {}
                for param in parent1_params:
                    if isinstance(parent1_params[param], int):
                        child_params[param] = random.choice([parent1_params[param], parent2_params[param]])
                    else:
                        child_params[param] = (parent1_params[param] + parent2_params[param]) / 2
                child['indicators'][indicator] = child_params
                child['weights'][indicator] = (parent1['weights'][indicator] + parent2['weights'][indicator]) / 2
            else:
                # Если индикатор есть только у одного родителя, берём его параметры
                parent = parent1 if indicator in parent1['indicators'] else parent2
                child['indicators'][indicator] = parent['indicators'][indicator].copy()
                child['weights'][indicator] = parent['weights'][indicator]

        # Нормализуем веса
        total_weight = sum(child['weights'].values())
        for indicator in child['weights']:
            child['weights'][indicator] /= total_weight

        return child

    def mutate(self, strategy):
        """Мутация стратегии с большим разнообразием."""
        if random.random() < 0.2:  # Увеличиваем шанс мутации до 20%
            # Мутация параметров
            for indicator, params in strategy['indicators'].items():
                if indicator == 'rsi':
                    params['period'] += random.randint(-3, 3)
                    params['overbought'] += random.uniform(-8, 8)
                    params['oversold'] += random.uniform(-8, 8)
                    params['adx_threshold'] += random.uniform(-3, 3)
                elif indicator == 'macd':
                    params['fast_period'] += random.randint(-2, 2)
                    params['slow_period'] += random.randint(-3, 3)
                    params['signal_period'] += random.randint(-2, 2)
                elif indicator == 'bollinger':
                    params['period'] += random.randint(-5, 5)
                    params['std_dev'] += random.uniform(-0.5, 0.5)
                elif indicator == 'mean_reversion':
                    params['lookback_period'] += random.randint(-5, 5)
                    params['z_score_threshold'] += random.uniform(-0.5, 0.5)
                else:  # trend
                    params['lookback_period'] += random.randint(-5, 5)

            # Мутация весов
            for indicator in strategy['weights']:
                strategy['weights'][indicator] += random.uniform(-0.2, 0.2)
                strategy['weights'][indicator] = max(0.1, min(0.9, strategy['weights'][indicator]))

            # Нормализуем веса после мутации
            total_weight = sum(strategy['weights'].values())
            for indicator in strategy['weights']:
                strategy['weights'][indicator] /= total_weight

            # Добавление или удаление индикатора
            if random.random() < 0.1:  # 10% шанс изменения набора индикаторов
                current_indicators = list(strategy['indicators'].keys())
                if len(current_indicators) < 2 and random.random() < 0.5:  # Добавляем индикатор
                    available_indicators = [ind for ind in self.indicators if ind not in current_indicators]
                    if available_indicators:
                        new_indicator = random.choice(available_indicators)
                        if new_indicator == 'rsi':
                            strategy['indicators']['rsi'] = {
                                'period': random.randint(5, 20),
                                'overbought': random.uniform(60, 80),
                                'oversold': random.uniform(20, 40),
                                'adx_threshold': random.uniform(20, 30)
                            }
                        elif new_indicator == 'macd':
                            strategy['indicators']['macd'] = {
                                'fast_period': random.randint(8, 16),
                                'slow_period': random.randint(20, 30),
                                'signal_period': random.randint(5, 12)
                            }
                        elif new_indicator == 'bollinger':
                            strategy['indicators']['bollinger'] = {
                                'period': random.randint(10, 30),
                                'std_dev': random.uniform(1.5, 3.0)
                            }
                        elif new_indicator == 'mean_reversion':
                            strategy['indicators']['mean_reversion'] = {
                                'lookback_period': random.randint(10, 30),
                                'z_score_threshold': random.uniform(1.5, 3.0)
                            }
                        else:  # trend
                            strategy['indicators']['trend'] = {
                                'lookback_period': random.randint(20, 60)
                            }
                        strategy['weights'][new_indicator] = random.uniform(0.3, 0.7)
                        # Нормализуем веса
                        total_weight = sum(strategy['weights'].values())
                        for ind in strategy['weights']:
                            strategy['weights'][ind] /= total_weight
                elif len(current_indicators) > 1:  # Удаляем индикатор
                    indicator_to_remove = random.choice(current_indicators)
                    strategy['indicators'].pop(indicator_to_remove)
                    strategy['weights'].pop(indicator_to_remove)
                    # Нормализуем веса
                    total_weight = sum(strategy['weights'].values())
                    for ind in strategy['weights']:
                        strategy['weights'][ind] /= total_weight

        return strategy
