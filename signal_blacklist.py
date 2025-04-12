from trading_bot.logging_setup import setup_logging

logger = setup_logging('signal_blacklist')

class SignalBlacklist:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.blacklist = set()

    def add_to_blacklist(self, signal: dict):
        """Add a signal to the blacklist."""
        try:
            # Динамическая корректировка критериев на основе волатильности
            if self.volatility > 0.5 and signal.get('confidence', 1.0) < 0.7:
                self.blacklist.add(signal['id'])
                logger.info(f"Signal {signal['id']} added to blacklist due to high volatility")
            else:
                self.blacklist.add(signal['id'])
                logger.info(f"Signal {signal['id']} added to blacklist")
        except Exception as e:
            logger.error(f"Failed to add signal to blacklist: {str(e)}")
            raise

    def is_blacklisted(self, signal_id: str) -> bool:
        """Check if a signal is blacklisted."""
        try:
            is_blacklisted = signal_id in self.blacklist
            logger.info(f"Signal {signal_id} is{' ' if is_blacklisted else ' not '}blacklisted")
            return is_blacklisted
        except Exception as e:
            logger.error(f"Failed to check blacklist for signal {signal_id}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    blacklist = SignalBlacklist(market_state)
    signal = {'id': 'signal_123', 'confidence': 0.8}
    blacklist.add_to_blacklist(signal)
    result = blacklist.is_blacklisted('signal_123')
    print(f"Is signal blacklisted? {result}")
