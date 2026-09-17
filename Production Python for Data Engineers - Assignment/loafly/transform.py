"""Transform: Data cleaning, calculations, and domain model mapping."""

import logging

logger = logging.getLogger("loafly.transform")


def clean_price(text):
    """Safely convert a price string to a float. Returns None if invalid."""
    if text is None:
        return None
    try:
        cleaned = text.strip().replace(",", "")
        return float(cleaned)
    except (ValueError, AttributeError):
        return None


def apply_discount(price, percent):
    """Calculate price after percentage discount."""
    return price - (price * percent / 100)


def build_orders(rows):
    """Group raw rows into Order instances, skipping items with bad prices."""
    from loafly.models import Order

    orders = {}
    skipped_items = 0

    for row in rows:
        oid = row["order_id"]
        item_name = row["item_name"]
        raw_price = row.get("item_price")

        price = clean_price(raw_price)
        if price is None:
            logger.warning("Order %s: Skipping item '%s' due to invalid price %r", oid, item_name, raw_price)
            skipped_items += 1
            continue

        if oid not in orders:
            orders[oid] = Order(oid, row["customer"])
        
        orders[oid].add_item(item_name, price)

    logger.info("Transformed rows into %d orders (%d items skipped)", len(orders), skipped_items)
    return orders