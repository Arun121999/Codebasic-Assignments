"""
 Sync versus async. Fetch the result count for several subjects two ways: one at a time (sync), and all together with asyncio.gather and asyncio.to_thread (async). Time both and print the two timings. Acceptance criteria: a sync version and an async version, both timed; async is clearly faster across several calls. (Needs internet.)

****************************************************************

Fetch the result count (numFound) for several subjects two ways:
  1. sync   - one request at a time, in a plain loop
  2. async  - all requests fired together, using asyncio.gather +
              asyncio.to_thread (since requests.get is a blocking call,
              not natively async)
 
Both are timed with time.perf_counter() so we can compare.
"""

import asyncio
import time

import requests

BASE_URL = "https://openlibrary.org/search.json"
 
 
def fetch_count(subject, timeout=15):
    """
    Calls the Open Library search API for a subject and returns numFound
    (the total number of matching books). Returns None if the call fails,
    so one bad subject doesn't crash the whole batch.
    """
    url = f"{BASE_URL}?q={subject}&limit=1&fields=title"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data.get("num_found")
    except Exception as e:
        print(f"[fetch_count] '{subject}' failed ({e})")
        return None


def fetch_counts_sync(subjects):
    """One request at a time, waiting for each to finish before the next."""
    results = {}

    for subject in subjects:
        results[subject] = fetch_count(subject)
    
    return results

async def fetch_counts_async(subjects):
    """
    All requests fired together. requests.get is a blocking call, so we
    push each one onto a background thread with asyncio.to_thread, then
    await all of them together with asyncio.gather.
    """

    tasks = [asyncio.to_thread(fetch_count, subject) for subject in subjects]
    results_list = await asyncio.gather(*tasks)
    return dict(zip(subjects, results_list))


if __name__ == "__main__":
    subjects = ["python", "javascript", "rust", "data engineering", "machine learning"]
 
    print(f"Fetching result counts for {len(subjects)} subjects...\n")
 
    # --- Sync ---
    print("--- Sync (one at a time) ---")
    start = time.perf_counter()
    sync_results = fetch_counts_sync(subjects)
    sync_time = time.perf_counter() - start
    for subject, count in sync_results.items():
        print(f"  {subject}: {count}")
    print(f"Sync total time: {sync_time:.2f}s\n")


     # --- Async ---
    print("--- Async (all together) ---")
    start = time.perf_counter()
    async_results = asyncio.run(fetch_counts_async(subjects))
    async_time = time.perf_counter() - start
 
    for subject, count in async_results.items():
        print(f"  {subject}: {count}")
    print(f"Async total time: {async_time:.2f}s\n")
 
    # --- Comparison ---
    print("--- Comparison ---")
    print(f"Sync:  {sync_time:.2f}s")
    print(f"Async: {async_time:.2f}s")
    if async_time < sync_time:
        speedup = sync_time / async_time
        print(f"Async was {speedup:.1f}x faster across {len(subjects)} calls.")
    else:
        print("Async was not faster this run (unexpected -- check your "
              "internet connection or try more subjects).")