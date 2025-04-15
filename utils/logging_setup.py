import logging
import os
from datetime import datetime

# Словарь для хранения логгеров
_loggers = {}

def setup_logging(name):
    """Set up a logger with the given name."""
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Создаём обработчик для файла
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Создаём форматтер
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Добавляем обработчик к логгеру
    logger.addHandler(file_handler)

    _loggers[name] = logger
    return logger

def close_loggers():
    """Close all loggers and their handlers."""
    for name, logger in _loggers.items():
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    _loggers.clear()
