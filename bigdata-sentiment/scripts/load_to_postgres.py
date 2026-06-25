#!/usr/bin/env python3
"""
Loads cleaned YouTube comments from data/cleaned_comments.csv into PostgreSQL.
Creates the database and table if they don't already exist.

Run from the project root:
    python scripts/load_to_postgres.py
"""

import csv
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = Path(__file__).parent.parent / "data" / "cleaned_comments.csv"

DB_NAME = os.getenv("DB_NAME", "sentiment_db")
DB_PARAMS = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432)),
    dbname=DB_NAME,
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
)

INSERT_SQL = """
    INSERT INTO youtube_comments
        (video_id, video_title, comment_text, author, like_count, published_at)
    VALUES (%s, %s, %s, %s, %s, %s)
"""

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS youtube_comments (
    id              SERIAL PRIMARY KEY,
    video_id        VARCHAR(20)  NOT NULL,
    video_title     TEXT,
    comment_text    TEXT         NOT NULL,
    author          VARCHAR(255),
    like_count      INTEGER      DEFAULT 0,
    published_at    TIMESTAMPTZ,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(10),
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sentiment_label ON youtube_comments(sentiment_label);
CREATE INDEX IF NOT EXISTS idx_video_id        ON youtube_comments(video_id);
"""


def ensure_database():
    admin_params = {**DB_PARAMS, "dbname": "postgres"}
    try:
        conn = psycopg2.connect(**admin_params)
    except psycopg2.OperationalError as e:
        sys.exit(f"Cannot connect to PostgreSQL: {e}\nCheck your .env credentials.")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if not cur.fetchone():
        cur.execute(f'CREATE DATABASE "{DB_NAME}"')
        print(f"Created database: {DB_NAME}")
    else:
        print(f"Database '{DB_NAME}' already exists")
    cur.close()
    conn.close()


def parse_ts(ts_str: str):
    if not ts_str:
        return None
    try:
        from datetime import datetime
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def main():
    if not DATA_FILE.exists():
        sys.exit(f"Data file not found: {DATA_FILE}\nRun: python scripts/clean_comments.py first")

    records = []
    with open(DATA_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    print(f"Loaded {len(records)} records from {DATA_FILE.name}")

    ensure_database()

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute(CREATE_TABLE_SQL)
    cur.execute("TRUNCATE youtube_comments RESTART IDENTITY;")

    rows = [
        (
            r.get("videoId", ""),
            r.get("videoTitle", ""),
            r.get("comment", ""),
            r.get("author", ""),
            int(r.get("likeCount", 0) or 0),
            parse_ts(r.get("publishedAt", "")),
        )
        for r in records
    ]

    cur.executemany(INSERT_SQL, rows)
    conn.commit()
    print(f"Inserted {len(rows)} rows into youtube_comments")

    cur.execute("SELECT COUNT(*) FROM youtube_comments;")
    print(f"Table row count: {cur.fetchone()[0]}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
