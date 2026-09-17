# Loafly Orders Pipeline

ETL pipeline for parsing, cleaning, transforming, and uploading customer order batches.

## Setup Instructions

1. **Create and activate a virtual environment:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1


Task 1: Functions
-clean_price(text) in loafly/transform.py strips whitespace/commas and casts prices to float. 
-apply_discount(price, percent) calculates percentage discounts dynamically.

Task 2: OOP Modeling
-Order class in loafly/models.py encapsulates order_id, customer, and items. 
-Order total is calculated via Order.total().

Task 3: Modules and Packages
-Project split into the loafly package (config, models, extract, transform, load). run_pipeline.py orchestrates the extraction, transformation, and loading sequence.

Task 4: Config-Driven Design
-loafly/config.py centralizes all settings including file paths (RAW_ORDERS_PATH), currency (CURRENCY), discount -rates (DISCOUNT_PERCENT), and API retries (MAX_ATTEMPTS).

Task 5: Logging and Exception Handling
-All print calls replaced with structured logging to standard output and orders.log. 
-clean_price safely catches bad or blank values with try/except, logging warnings and skipping bad items without stopping execution.

Task 6: Retry, Environments and Secrets
-save_with_retry in loafly/load.py retries API calls up to MAX_ATTEMPTS before logging failure. LOAFLY_API_KEY is loaded from .env via python-dotenv. .env and orders.log are excluded via .gitignore.