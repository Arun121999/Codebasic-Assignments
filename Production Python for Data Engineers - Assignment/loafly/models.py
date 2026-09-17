"""Model: Core domain entities."""

from loafly.config import DISCOUNT_PERCENT
from loafly.transform import apply_discount


class Order:
    """Model a single customer order."""

    def __init__(self, order_id, customer):
        self.order_id = order_id
        self.customer = customer
        self.items = []

    def add_item(self, name, price):
        """Add a valid item to the order."""
        self.items.append((name, price))

    def total(self):
        """Calculate order total with discount applied."""
        subtotal = sum(price for _, price in self.items)
        return apply_discount(subtotal, DISCOUNT_PERCENT)