"""UK business-news crawler.

Reads The Guardian's Business RSS feed (UK-focused, free, stable) instead of
scraping HTML — RSS is far less brittle than the old LTN page scraper. Exposes
``crawl_news()`` as a plain function so it can be called from a route, a
scheduled job, or a test. Old (LTN) rows already in the store are kept; this
just adds the latest UK headlines.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests

NEWS_URL = "https://www.theguardian.com/uk/business/rss"
_MEDIA_NS = {"media": "http://search.yahoo.com/mrss/"}


def _image_url(item: ET.Element) -> str | None:
    """Pick an image from <media:content> or <enclosure>, if present."""
    medias = item.findall("media:content", _MEDIA_NS)
    if medias:
        # Prefer a mid-size image; fall back to the first.
        best = max(medias, key=lambda m: int(m.get("width") or 0))
        return best.get("url")
    enc = item.find("enclosure")
    return enc.get("url") if enc is not None else None


def _format_date(pub: str | None) -> str:
    if not pub:
        return ""
    try:
        return parsedate_to_datetime(pub).strftime("%Y/%m/%d %H:%M")
    except (TypeError, ValueError):
        return ""


def crawl_news(url: str = NEWS_URL, timeout: int = 15) -> list[dict]:
    """Fetch the latest UK business headlines as a list of dicts.

    Each item: ``{"title", "link", "date", "image_url"}``. Returns an empty list
    if the request or parse fails, so callers never crash on a network hiccup.
    """
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        res.raise_for_status()
        root = ET.fromstring(res.content)
    except (requests.RequestException, ET.ParseError):
        return []

    items = []
    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not title or not link:
            continue
        items.append(
            {
                "title": title,
                "link": link,
                "date": _format_date(item.findtext("pubDate")),
                "image_url": _image_url(item),
            }
        )
    return items


if __name__ == "__main__":
    # Manual smoke test: python -m focusedgroup.news.crawler
    for row in crawl_news():
        print(row["date"], "|", row["title"])
