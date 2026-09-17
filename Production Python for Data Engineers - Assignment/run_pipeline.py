"""Runner: Pipeline orchestrator."""

import logging
import sys
from loafly.config import API_KEY, LOG_FILE
from loafly.extract import extract_rows
from loafly.transform import build_orders
from loafly.load import save_orders

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("runner")


def main():
    if not API_KEY:
        logger.error("LOAFLY_API_KEY is not set. Copy env.example to .env and set your key.")
        sys.exit(1)

    logger.info("Starting Loafly Order Processing Pipeline")
    rows = extract_rows()
    orders = build_orders(rows)
    save_orders(orders)


if __name__ == "__main__":
    main()