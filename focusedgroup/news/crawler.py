"""UK + US stock-market news crawler.

Reads RSS feeds (no scraping — far less brittle):
  * The Guardian Business (UK, includes images)
  * Yahoo Finance S&P 500 headlines (US markets)

Exposes ``crawl_news()`` as a plain function so it can be called from a route, a
scheduled job, or a test. Old rows already in the store are kept; this just adds
the latest market headlines.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests

# (feed url, label) — UK first, then US markets.
FEEDS = [
    ("https://www.theguardian.com/uk/business/rss", "Guardian"),
    (
        "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EGSPC&region=US&lang=en-US",
        "Yahoo Finance",
    ),
]
_MEDIA_NS = {"media": "http://search.yahoo.com/mrss/"}


def _image_url(item: ET.Element) -> str | None:
    medias = item.findall("media:content", _MEDIA_NS)
    if medias:
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


def _parse_feed(url: str, timeout: int) -> list[dict]:
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


def crawl_news(timeout: int = 15) -> list[dict]:
    """Fetch the latest UK + US market headlines, merged across feeds.

    Each item: ``{"title", "link", "date", "image_url"}`` (image may be None for
    feeds without media). Returns whatever feeds succeed; never raises.
    """
    items: list[dict] = []
    for url, _label in FEEDS:
        items.extend(_parse_feed(url, timeout))
    return items


if __name__ == "__main__":
    # Manual smoke test: python -m focusedgroup.news.crawler
    for row in crawl_news():
        print(row["date"], "|", row["title"])
