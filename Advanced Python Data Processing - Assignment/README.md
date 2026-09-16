# Advanced Python Data Processing - Assignment (Session 5)

Setup:

```
pip install -r requirements.txt
```
## Task 1 - get_books (Python-Assignment-Task-1.py)

`get_books(subject, page)` calls Open Library's search API and returns
title, author, first publish year and rating for each book. Has a
timeout and a try/except fallback.

```
python Python-Assignment-Task-1.py
```

## Task 2 - pagination + watermark (Python-Assignment-Task-2.py)

`full_load(subject, page_cap)` pages through `get_books()` until a page
is empty or `page_cap` is hit. `compute_watermark(books)` finds the
newest `first_publish_year` seen. `incremental_filter(books, watermark)`
keeps only books newer than that.

```
python Python-Assignment-Task-2.py
```

## Task 3 - sync vs async (Python-Assignment-Task-3.py)

Fetches `numFound` for 5 subjects two ways: one at a time
(`fetch_counts_sync`) and all together with `asyncio.gather` +
`asyncio.to_thread` (`fetch_counts_async`). Times both.

```
python Python-Assignment-Task-3.py
```

## Task 4 - serial vs parallel (Python-Assignment-Task-4.py)

`score_genre(genre)` is a CPU-heavy dummy function. Runs once serially,
once in parallel with `ProcessPoolExecutor` + `pool.map`. Times both and
checks the results match.

```
python Python-Assignment-Task-4.py
```

## Task 5 - streaming + memory (Python-Assignment-Task-5.py)

`stream_revenue_by_genre` reads `data/sales.csv` in chunks and totals
revenue by genre without loading the whole file. `shrink_chunk_memory`
downcasts one chunk (`float32`, `category`) and compares memory before
and after.

```
python Python-Assignment-Task-5.py
```

## Task 6 - pytest for pricing.py (test_pricing.py)

Tests for `member_price`, `add_gst`, `delivery_fee`, `loyalty_points` -

pytest -v
