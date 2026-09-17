"""Gateway API client mock."""
import logging

logger = logging.getLogger("gateway")


def save_to_orders_api(order_id, total):
    """Simulate saving an order to the API."""
    return True