"""Extract: Ingest raw data from CSV sources."""

import csv
import logging
from loafly.config import RAW_ORDERS_PATH

logger = logging.getLogger("loafly.extract")


def extract_rows(path=RAW_ORDERS_PATH):
    """Read CSV rows into a list of dicts."""
    try:
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            logger.info("Loaded %d rows from %s", len(rows), path)
            return rows
    except OSError:
        logger.error("Failed to open input file: %s", path, exc_info=True)
        raise