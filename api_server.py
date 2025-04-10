from flask import Flask, request, jsonify
from core import TradingBot
from user_manager import UserManager
import jwt
from logging_setup import setup_logging
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure key
user_manager = UserManager()
bots = {}  # Store bots per user
logger = setup_logging('api_server')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            logger.warning("Token is missing")
            return jsonify({"error": "Token is missing"}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = data['user_id']
        except Exception as e:
            logger.error(f"Invalid token: {str(e)}")
            return jsonify({"error": "Invalid token"}), 401
        return f(user_id, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        user_id = data.get('user_id')
        password = data.get('password')
        if user_manager.authenticate_user(user_id, password):
            token = jwt.encode({'user_id': user_id}, app.config['SECRET_KEY'], algorithm='HS256')
            logger.info(f"User {user_id} logged in")
            return jsonify({"token": token})
        else:
            logger.warning(f"Failed login attempt for user {user_id}")
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/start', methods=['POST'])
@token_required
def start_bot(user_id):
    try:
        symbols = user_manager.get_user(user_id).get('symbols', ['BTC/USDT'])
        bot = TradingBot('binance', symbols)
        bots[user_id] = bot
        bot.start()
        logger.info(f"Bot started for user {user_id}")
        return jsonify({"status": "Bot started"})
    except Exception as e:
        logger.error(f"Failed to start bot for user {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/stop', methods=['POST'])
@token_required
def stop_bot(user_id):
    try:
        bot = bots.get(user_id)
        if bot:
            bot.stop()
            logger.info(f"Bot stopped for user {user_id}")
            return jsonify({"status": "Bot stopped"})
        else:
            logger.warning(f"No bot found for user {user_id}")
            return jsonify({"error": "Bot not found"}), 404
    except Exception as e:
        logger.error(f"Failed to stop bot for user {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
@token_required
def get_status(user_id):
    try:
        bot = bots.get(user_id)
        if bot:
            status = bot.get_status()
            logger.info(f"Status for user {user_id}: {status}")
            return jsonify({"status": status})
        else:
            logger.warning(f"No bot found for user {user_id}")
            return jsonify({"error": "Bot not found"}), 404
    except Exception as e:
        logger.error(f"Failed to get status for user {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
