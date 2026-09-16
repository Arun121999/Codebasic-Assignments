"""
Ingestion: pagination and incremental. Loop through the pages to pull the books for a subject (a full load, with a sensible page cap). Then keep a watermark (the newest publish year you saw) and show how the next run would pull only books newer than that (incremental). Acceptance criteria: a loop that pages until an empty page or the cap; a full load count; a watermark and an incremental filter that uses it.


************************************************************************
full_load(subject, page_cap) pages through get_books() until a page comes back empty or we hit the page cap, collecting every book along the way.

We then compute a watermark = the newest first_publish_year seen in that load. incremental_filter(books, watermark) shows how the *next* run would only keep books newer than that watermark, instead of re-pulling everything.
"""
import json
from pathlib import Path

import requests

BASE_URL = "https://openlibrary.org/search.json"
FIELDS = "title,author_name,first_publish_year,ratings_average,edition_count"
OFFLINE_FILE = Path(__file__).parent / "data" / "offline_books.json"


def load_offlin_books():
    with open(OFFLINE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_books(subject, page, limit=10, timeout=15):
    url = f"{BASE_URL}?q={subject}&page={page}&limit={limit}&fields={FIELDS}"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # here this line will check that is there any issue in the error means received unwanted status code. But if its 200 then it will do nothing
        data = response.json()

        docs = data.get('docs', [])

        books = []

        for doc in docs:
            books.append({
                "title": doc.get("title"),
                "author": doc.get("author_name", ["Unknown"])[0] if doc.get("author_name") else "Unknown",
                "first_publish_year": doc.get("first_publish_year"),
                "rating": doc.get("ratings_average")
            })

        return books

    except Exception as e:
        print(f"[get_books] API call failed ({e}). Falling back to offline sample.")
        offline_books = load_offlin_books()
        books = []
        for b in offline_books:
            books.append({
                "title": b.get("title"),
                "author": b.get("author_name", ["Unknown"])[0] if b.get("author_name") else "Unknown",
                "first_publish_year": b.get("first_publish_year"),
                "rating": b.get("ratings_average")
            })

        return books


def full_load(subject, page_cap=10, limit=10):
    all_books = []
    page = 1

    while page <= page_cap:
        books = get_books(subject, page, limit=limit)

        if not books:
            print(f"Page was empty: {page} (stopping)")
            break

        all_books.extend(books)
        print(f"Books Added")

        page += 1

    else:
        print(f"[full_load] Hit page cap ({page_cap}). Stopping.")

    return all_books


def compute_watermark(books):
    """
    The watermark is the newest first_publish_year seen across the load.
    None values are ignored, since a missing year can't be "newer" than
    anything.
    """
    years = [b["first_publish_year"] for b in books if b["first_publish_year"]]
    print(years)
    if not years:
        return None

    return max(years)


def incremental_filter(books, watermark):

    # Here if the watermark is none then we return the books as it is
    if watermark is None:
        return books

    # Here if the watermark is not none then we compare the watermark with the first_publish_year
    return [b for b in books if b["first_publish_year"] and b["first_publish_year"] > watermark]


if __name__ == "__main__":
    subject = "Learning Python"
    page_cap = 10

    print(f"--- Full load for subject='{subject}' (page cap={page_cap}) ---")
    books = full_load(subject, page_cap=page_cap)
    print(f"\nFull-load count: {len(books)} books\n")

    watermark = compute_watermark(books)
    print(f"Watermark (newest first_publish_year seen): {watermark}\n")

    print("--- Simulating next run: incremental load ---")
    new_books = incremental_filter(books, watermark)
    print(f"Books newer than watermark ({watermark}): {len(new_books)}")
    for b in new_books:
        print(f"  - {b['title']} ({b['first_publish_year']})")

    if not new_books:
        print("  (none -- expected, since watermark = max year already seen "
              "this run; a real next run would find new books published "
              "after today.)")
