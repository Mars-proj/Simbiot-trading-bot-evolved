import logging
import os
from datetime import datetime

def setup_logging(module_name: str) -> logging.Logger:
    """Set up logging for a module."""
    try:
        # Создаём директорию для логов, если её нет
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Формируем имя файла лога с текущей датой
        log_file = os.path.join(log_dir, f"{module_name}_{datetime.now().strftime('%Y%m%d')}.log")

        # Настраиваем логгер
        logger = logging.getLogger(module_name)
        logger.setLevel(logging.INFO)

        # Создаём обработчик для файла
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)

        # Создаём обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Формат логов
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Добавляем обработчики к логгеру
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.info(f"Logging setup completed for {module_name}")
        return logger
    except Exception as e:
        print(f"Failed to setup logging for {module_name}: {str(e)}")
        raise

if __name__ == "__main__":
    # Test run
    logger = setup_logging("test_module")
    logger.info("This is a test log message")
