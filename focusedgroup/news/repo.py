"""SQLite-backed store for news items — the single entry point for reading and
writing news. Routes and jobs talk to this, never to the CSV/DB directly.

Swapping to Postgres later means changing only this file.
"""

import sqlite3
from pathlib import Path

# data/news.db at the project root (this file is focusedgroup/news/repo.py)
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "news.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    title     TEXT NOT NULL,
    link      TEXT NOT NULL UNIQUE,
    date      TEXT,
    image_url TEXT
);
"""


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


def save_news(items: list[dict], db_path: Path = DB_PATH) -> int:
    """Upsert items by their unique link. Returns the number written."""
    if not items:
        return 0
    init_db(db_path)
    with _connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO news (title, link, date, image_url)
            VALUES (:title, :link, :date, :image_url)
            ON CONFLICT(link) DO UPDATE SET
                title = excluded.title,
                date = excluded.date,
                image_url = excluded.image_url
            """,
            items,
        )
    return len(items)


def get_latest(limit: int = 30, db_path: Path = DB_PATH) -> list[dict]:
    """Return the most recent news items, newest first."""
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT title, link, date, image_url FROM news "
            "ORDER BY date DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
