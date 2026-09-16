"""
Serial versus parallel. Run a CPU-heavy per-genre scoring job serially, then
across cores with ProcessPoolExecutor and pool.map (parallel). Time both and
confirm the results match. Acceptance criteria: both versions timed;
identical results either way; note your machine's core count, and on a
multi-core machine parallel is faster.

********************************************************************
score_genre(genre) is a deliberately CPU-heavy function (lots of raw
number-crunching, no waiting). We run it once serially (one genre at a
time), and once in parallel across CPU cores using ProcessPoolExecutor +
pool.map. Both are timed, and we confirm both approaches give identical
results -- only the execution strategy differs, not the math.

score_genre must live at the top level of the file (not nested inside
another function) so it can be pickled and sent to worker processes.
"""

import os
import time
from concurrent.futures import ProcessPoolExecutor

GENRES = [
    "Fiction", "Mystery", "Sci-Fi", "Romance",
    "Fantasy", "Thriller", "Biography", "History",
]


def score_genre(genre):
    """
    Deliberately CPU-heavy "popularity score" for a genre. There's nothing
    meaningful about the math here -- it exists purely to burn CPU cycles
    so serial vs parallel timing actually shows a difference.
    """
    total = 0
    for i in range(10_000_000):
        total += (i * len(genre)) % 7919  # 7919 is just an arbitrary prime
    return genre, total


def run_serial(genres):
    """One genre at a time, on a single core."""
    return [score_genre(g) for g in genres]


def run_parallel(genres):
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(score_genre, genres))
    return results


if __name__ == "__main__":
    core_count = os.cpu_count()
    print(f"Machine core count: {core_count}\n")

    # --- Serial ---
    print("--- Serial (one genre at a time) ---")
    start = time.perf_counter()
    serial_results = run_serial(GENRES)
    serial_time = time.perf_counter() - start
    print(f"Serial time: {serial_time:.2f}s\n")

    # --- Parallel ---
    print("--- Parallel (across cores) ---")
    start = time.perf_counter()
    parallel_results = run_parallel(GENRES)
    parallel_time = time.perf_counter() - start
    print(f"Parallel time: {parallel_time:.2f}s\n")

    # --- Confirm identical results ---
    results_match = serial_results == parallel_results
    print(f"Results identical: {results_match}")

    # --- Comparison ---
    print("\n--- Comparison ---")
    print(f"Serial:   {serial_time:.2f}s")
    print(f"Parallel: {parallel_time:.2f}s")
    if core_count and core_count > 1:
        if parallel_time < serial_time:
            speedup = serial_time / parallel_time
            print(f"Parallel was {speedup:.1f}x faster "
                  f"(machine has {core_count} cores).")
        else:
            print("Parallel wasn't faster this run -- on a small job, "
                  "process start-up overhead can outweigh the benefit. "
                  "Try increasing the work in score_genre.")
    else:
        print("Single-core machine detected -- parallel speedup isn't "
              "expected here.")