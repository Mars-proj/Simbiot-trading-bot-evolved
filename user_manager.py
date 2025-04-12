from trading_bot.logging_setup import setup_logging

logger = setup_logging('user_manager')

class UserManager:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.users = {}

    def add_user(self, user_id: str, balance: float):
        """Add a user with an initial balance."""
        try:
            # Динамическая корректировка баланса на основе волатильности
            adjusted_balance = balance * (1 - self.volatility / 2)
            
            self.users[user_id] = {
                'balance': adjusted_balance,
                'positions': []
            }
            logger.info(f"User {user_id} added with adjusted balance {adjusted_balance}")
        except Exception as e:
            logger.error(f"Failed to add user {user_id}: {str(e)}")
            raise

    def update_balance(self, user_id: str, amount: float):
        """Update a user's balance."""
        try:
            if user_id not in self.users:
                raise ValueError(f"User {user_id} not found")
            
            self.users[user_id]['balance'] += amount
            logger.info(f"User {user_id} balance updated to {self.users[user_id]['balance']}")
        except Exception as e:
            logger.error(f"Failed to update balance for user {user_id}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    manager = UserManager(market_state)
    manager.add_user('user_123', 10000)
    manager.update_balance('user_123', 500)
    print(f"User data: {manager.users['user_123']}")
