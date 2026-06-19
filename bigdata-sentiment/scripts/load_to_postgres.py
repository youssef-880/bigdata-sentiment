#!/usr/bin/env python3
"""
Loads cleaned YouTube comments from the HDFS-output JSONL file into PostgreSQL.

Connection: Unix socket peer auth (runs as hex OS user → hex DB role).
Run from your terminal:
    python3 scripts/load_to_postgres.py
"""

import json
import sys
from pathlib import Path
import psycopg2
from datetime import datetime, timezone

DATA_FILE = Path(__file__).parent.parent / "data" / "cleaned_comments.jsonl"

DB_PARAMS = dict(
    host="127.0.0.1",
    port=5432,
    dbname="sentiment_project",
    user="hex",
    password="hexpass",
)

INSERT_SQL = """
    INSERT INTO youtube_comments
        (video_id, video_title, comment_text, author, like_count, published_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING
"""


def parse_ts(ts_str: str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def main():
    if not DATA_FILE.exists():
        sys.exit(f"Data file not found: {DATA_FILE}")

    records = []
    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                records.append(r)
            except json.JSONDecodeError:
                continue

    print(f"Loaded {len(records)} records from {DATA_FILE.name}")

    try:
        conn = psycopg2.connect(**DB_PARAMS)
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        print("Make sure you've run: sudo -u postgres psql -f sql/schema.sql")
        sys.exit(1)

    cur = conn.cursor()

    # Clear existing data so re-runs are idempotent
    cur.execute("TRUNCATE youtube_comments RESTART IDENTITY;")

    rows = [
        (
            r.get("videoId", ""),
            r.get("videoTitle", ""),
            r.get("comment", ""),
            r.get("author", ""),
            r.get("likeCount", 0),
            parse_ts(r.get("publishedAt", "")),
        )
        for r in records
    ]

    cur.executemany(INSERT_SQL, rows)
    conn.commit()
    print(f"Inserted {cur.rowcount if cur.rowcount >= 0 else len(rows)} rows into youtube_comments")

    cur.execute("SELECT COUNT(*) FROM youtube_comments;")
    count = cur.fetchone()[0]
    print(f"Table now has {count} rows")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
