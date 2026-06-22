"""Business-news crawler.

Exposes ``crawl_news()`` as a plain function so it can be called from a route,
a scheduled job, or a test — instead of running on import like the old script.
"""

from datetime import date, datetime

import requests
from bs4 import BeautifulSoup

NEWS_URL = "https://news.ltn.com.tw/list/breakingnews/business"


def crawl_news(url: str = NEWS_URL, timeout: int = 10) -> list[dict]:
    """Fetch the latest business headlines and return them as a list of dicts.

    Each item: ``{"title", "link", "date", "image_url"}``.
    Returns an empty list if the request fails, so callers never crash on a
    network hiccup.
    """
    try:
        res = requests.get(url, timeout=timeout)
        res.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    items = []

    for node in soup.select("ul.list > li"):
        anchor = node.select_one("a")
        if anchor is None:
            continue

        title = (anchor.get("title") or "").strip()
        link = anchor.get("href", "")
        if not title or not link:
            continue

        # The list only carries HH:MM; pin it to today's date.
        time_node = node.select_one("span.time")
        time_str = time_node.text.strip() if time_node else ""
        try:
            t = datetime.strptime(time_str, "%H:%M").time()
            published = datetime.combine(date.today(), t).strftime("%Y/%m/%d %H:%M")
        except ValueError:
            published = ""

        img = node.select_one("img")
        image_url = img.get("data-src") if img is not None else None

        items.append(
            {
                "title": title,
                "link": link,
                "date": published,
                "image_url": image_url,
            }
        )

    return items


if __name__ == "__main__":
    # Manual smoke test: python -m focusedgroup.news.crawler
    for row in crawl_news():
        print(row)
