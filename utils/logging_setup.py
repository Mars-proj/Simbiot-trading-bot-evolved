import logging
import os
from datetime import datetime

def setup_logging(name: str) -> logging.Logger:
    """Set up logging with a specified name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Создаём директорию для логов, если её нет
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Формат имени файла лога: logs/name_YYYY-MM-DD.log
    log_filename = os.path.join(log_dir, f"{name}_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Настраиваем обработчик для файла
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Настраиваем обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

if __name__ == "__main__":
    # Test run
    logger = setup_logging('test')
    logger.info("This is a test log message")
