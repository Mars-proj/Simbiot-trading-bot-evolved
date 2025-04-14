from utils.logging_setup import setup_logging

logger = setup_logging('websocket_manager')

class WebSocketManager:
    def __init__(self):
        pass

    def connect(self, exchange):
        logger.info(f"Connecting WebSocket to {exchange}")
        return True
