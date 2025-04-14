from utils.logging_setup import setup_logging

logger = setup_logging('volume_analyzer')

class VolumeAnalyzer:
    def __init__(self):
        pass

    def analyze(self, klines):
        logger.info("Analyzing volume")
        return sum(kline[5] for kline in klines) / len(klines) if klines else 0
