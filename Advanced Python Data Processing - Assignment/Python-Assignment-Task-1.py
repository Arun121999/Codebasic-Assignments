"""
APIs. Write a function get_books(subject, page) that calls the Open Library search API with requests and returns a list of books, each with its title, author, first publish year and rating. Give the call a timeout and wrap it in try/except so a failed call does not crash the script. Acceptance criteria: get_books returns a list of book dicts; the request has a timeout and error handling; running the script prints a few books.


************************************************************************
get_books(subject, page) calls the Open Library search API and returns a
list of book dicts: title, author, first publish year, rating.

If the API call fails (no internet, timeout, bad response), we fall back to
the local offline_books.json sample so the script never dead-ends.
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


if __name__ == "__main__":
    subject = "python"
    page = 1

    books = get_books(subject, page)
    for book in books:
        print(
            f"- {book['title']} "
            f"by {book['author']} "
            f"({book['first_publish_year']}) "
            f"rating={book['rating']}"
        )
