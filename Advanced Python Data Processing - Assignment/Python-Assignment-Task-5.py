"""
File streaming and memory. Stream sales.csv with pd.read_csv(chunksize=...) to total revenue by genre without ever loading the whole file. Then take one chunk and shrink its memory using float32 and the the memory before and after with category type, and report memory_usage(deep=True). Acceptance criteria: a chunked aggregate over the full file; a measurable memory reduction from the better data 
types.
**********************************************************************
Part 1: Stream sales.csv in chunks with pd.read_csv(chunksize=...) and
total revenue by genre, without ever holding the whole file in memory
at once.

Part 2: Take a single chunk, shrink its memory footprint using float32
(for price/rating) and category (for genre/city/payment_type), and
report memory_usage(deep=True) before and after.
"""

from pathlib import Path

import pandas as pd

# Path to the sales data file, built relative to this script's own location
SALES_FILE = Path(__file__).parent / "data" / "sales.csv"

# How many rows to read into memory at a time when streaming the CSV
CHUNK_SIZE = 50_000


def stream_revenue_by_genre(csv_path, chunk_size=CHUNK_SIZE):
    running_totals = pd.Series(dtype="float64")

    chunk_count = 0
    row_count = 0

    # pd.read_csv(..., chunksize=...) returns an iterator: each loop turn
    # gives us ONE chunk (a small DataFrame), not the whole file at once.
    # Once we move to the next chunk, the previous one is discarded from
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        chunk_count += 1
        row_count += len(chunk)

        # Add a new column: revenue earned per row = price * quantity sold
        chunk['revenue'] = chunk['price'] * chunk['quantity']

        # Group this chunk's rows by genre, and sum revenue within each group
        chunk_totals = chunk.groupby("genre")["revenue"].sum()

        # Merge this chunk's totals into the running totals.
        # fill_value=0 means: if a genre is new (not seen before) or missing
        running_totals = running_totals.add(chunk_totals, fill_value=0)

    return running_totals, chunk_count, row_count


def shrink_chunk_memory(chunk):
    """
    Takes one chunk and shrinks it using float32 for numeric columns and
    category for repeating text columns. Returns the memory usage before
    and after, in bytes.
    """
    # Measure memory usage BEFORE any dtype changes.
    # deep=True is required to get an accurate size for text/object columns
    # (without it, pandas under-reports string memory usage).
    before_bytes = chunk.memory_usage(deep=True).sum()

    # Work on a copy, so the original chunk is untouched and we can still
    shrunk = chunk.copy()

    # float64 (pandas default) -> float32: half the memory per number,
    # with more precision than price/rating actually need.
    shrunk["price"] = shrunk["price"].astype("float32")
    shrunk["rating"] = shrunk["rating"].astype("float32")

    # object (plain text) -> category: these columns repeat the same small
    # payment types). category stores each unique value once and points
    # to it with a small code, instead of repeating the full string per row.
    shrunk["genre"] = shrunk["genre"].astype("category")
    shrunk["city"] = shrunk["city"].astype("category")
    shrunk["payment_type"] = shrunk["payment_type"].astype("category")

    # Measure memory usage AFTER the conversions, using the same method,
    after_bytes = shrunk.memory_usage(deep=True).sum()

    return before_bytes, after_bytes, shrunk


if __name__ == "__main__":
    print(f"--- Streaming {SALES_FILE.name} in chunks of {CHUNK_SIZE:,} rows ---\n")

    # Run the full streaming aggregation across the entire file
    revenue_by_genre, chunk_count, row_count = stream_revenue_by_genre(SALES_FILE)

    print("--- Total revenue by genre ---")
    # sort_values(ascending=False): show biggest revenue genre first
    # .items(): loop over the Series as (genre, revenue) pairs, like a dict
    for genre, revenue in revenue_by_genre.sort_values(ascending=False).items():
        # :,.2f -> format with thousands-separator commas, 2 decimal places
        print(f"  {genre}: {revenue:,.2f}")

    print("\n--- Memory optimization demo (one chunk) ---")
    # pd.read_csv(..., chunksize=...) gives an iterator; next() grabs just
    # the FIRST chunk from it, without looping through the whole file again
    one_chunk = next(pd.read_csv(SALES_FILE, chunksize=CHUNK_SIZE))

    before_bytes, after_bytes, shrunk = shrink_chunk_memory(one_chunk)

    # What fraction of memory was saved, as a percentage:
    # (after_bytes / before_bytes) = fraction of memory REMAINING
    # 1 - that fraction = fraction of memory REMOVED
    # * 100 = convert to a percentage
    reduction_pct = (1 - after_bytes / before_bytes) * 100

    print(f"Before: {before_bytes:,} bytes ({before_bytes / 1024:.1f} KB)")
    print(f"After:  {after_bytes:,} bytes ({after_bytes / 1024:.1f} KB)")
    print(f"Reduction: {reduction_pct:.1f}%")

    print("\nDtypes before -> after:")
    for col in ["price", "rating", "genre", "city", "payment_type"]:
        print(f"  {col}: {one_chunk[col].dtype} -> {shrunk[col].dtype}")