import logging
import os

def setup_logging(module_name: str):
    """Set up logging for a module."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{module_name}.log")

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    # Create file handler
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(fh)

    return logger
