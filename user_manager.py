import sqlite3
from logging_setup import setup_logging

logger = setup_logging('user_manager')

class UserManager:
    def __init__(self):
        self.db_path = "users.db"
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    password TEXT,
                    symbols TEXT
                )
            ''')
            # Add a default user for testing
            cursor.execute('INSERT OR IGNORE INTO users (user_id, password, symbols) VALUES (?, ?, ?)',
                           ('user1', 'password1', 'BTC/USDT,ETH/USDT'))
            conn.commit()

    def authenticate_user(self, user_id: str, password: str) -> bool:
        """Authenticate a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT password FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                if result and result[0] == password:
                    logger.info(f"User {user_id} authenticated successfully")
                    return True
                logger.warning(f"Authentication failed for user {user_id}")
                return False
        except Exception as e:
            logger.error(f"Authentication error for user {user_id}: {str(e)}")
            raise

    def get_user(self, user_id: str) -> dict:
        """Get user settings."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT symbols FROM users WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()
                if result:
                    symbols = result[0].split(',') if result[0] else []
                    logger.info(f"Retrieved settings for user {user_id}: {symbols}")
                    return {"symbols": symbols}
                logger.warning(f"User {user_id} not found")
                return {}
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {str(e)}")
            raise
