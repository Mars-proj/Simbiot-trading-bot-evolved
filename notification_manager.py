from telegram_notifier import send_telegram_message
from logging_setup import setup_logging

logger = setup_logging('notification_manager')

def notify(message: str, channel: str = "telegram"):
    """Send a notification through the specified channel."""
    try:
        if channel == "telegram":
            send_telegram_message(message)
            logger.info(f"Sent notification via {channel}: {message}")
        else:
            logger.warning(f"Unsupported notification channel: {channel}")
            raise ValueError(f"Unsupported channel: {channel}")
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        raise
