"""Refresh the news store: crawl the latest headlines and save them to SQLite.

Run manually (`python news.py`) or from a scheduler. This replaces the old
import-time script that wrote a big5-encoded news.csv.
"""

from focusedgroup.news.crawler import crawl_news
from focusedgroup.news.repo import save_news


def main() -> None:
    items = crawl_news()
    saved = save_news(items)
    print(f"Saved {saved} news items.")


if __name__ == "__main__":
    main()
