"""Config: Centralized settings and environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LOAFLY_API_KEY")
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 1

CURRENCY = "INR"
DISCOUNT_PERCENT = 10
RAW_ORDERS_PATH = "raw_orders.csv"
LOG_FILE = "orders.log"