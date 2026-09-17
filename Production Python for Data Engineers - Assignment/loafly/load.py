"""Load: Output processing results and communicate with API gateway."""

import logging
import time
from loafly.config import CURRENCY, MAX_ATTEMPTS, RETRY_DELAY_SECONDS
from gateway import save_to_orders_api

logger = logging.getLogger("loafly.load")


def save_with_retry(order_id, total):
    """Attempt saving an order to the API with retry logic."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            return save_to_orders_api(order_id, total)
        except ConnectionError as e:
            logger.warning(
                "Order %s: Save attempt %d/%d failed - %s",
                order_id, attempt, MAX_ATTEMPTS, e
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)
    return None


def save_orders(orders):
    """Process and save all orders."""
    processed = 0
    failed_saves = 0

    for oid, order in orders.items():
        order_total = order.total()
        result = save_with_retry(oid, order_total)

        if result is None:
            failed_saves += 1
            logger.error("Failed to save order %s after %d attempts", oid, MAX_ATTEMPTS)
        else:
            logger.info("Saved order %s for %s - total: %.2f %s", oid, order.customer, order_total, CURRENCY)
            processed += 1

    logger.info("Pipeline complete: %d orders saved, %d failed saves", processed, failed_saves)