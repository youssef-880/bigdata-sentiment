#!/usr/bin/env python3
"""
Reads apple_youtube_comments.json, keeps only English comments,
cleans text, and saves data/cleaned_comments.csv.

Run from the project root:
    python scripts/clean_comments.py
"""

import json
import re
import csv
from pathlib import Path

from langdetect import detect, LangDetectException

DATA_DIR = Path(__file__).parent.parent / "data"
INPUT_FILE = DATA_DIR / "apple_youtube_comments.json"
OUTPUT_FILE = DATA_DIR / "cleaned_comments.csv"

URL_RE = re.compile(r"https?://\S+|www\.\S+")
SPECIAL_RE = re.compile(r"[^a-zA-Z0-9\s'.,!?]")
WHITESPACE_RE = re.compile(r"\s+")

CSV_FIELDS = ["videoId", "videoTitle", "comment", "author", "likeCount", "publishedAt"]


def clean_text(text: str) -> str:
    text = URL_RE.sub(" ", text)
    text = SPECIAL_RE.sub(" ", text)
    text = WHITESPACE_RE.sub(" ", text).strip()
    return text


def is_english(text: str) -> bool:
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False


def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        records = json.load(f)

    total = len(records)
    kept = []
    filtered = 0

    for r in records:
        raw = r.get("comment", "").strip()
        if not raw:
            filtered += 1
            continue
        if not is_english(raw):
            filtered += 1
            continue
        cleaned = clean_text(raw)
        if not cleaned:
            filtered += 1
            continue
        kept.append({
            "videoId":     r.get("videoId", ""),
            "videoTitle":  r.get("videoTitle", ""),
            "comment":     cleaned,
            "author":      r.get("author", ""),
            "likeCount":   r.get("likeCount", 0),
            "publishedAt": r.get("publishedAt", ""),
        })

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(kept)

    print(f"Total comments  : {total}")
    print(f"Kept (English)  : {len(kept)}")
    print(f"Filtered out    : {filtered}")
    print(f"Output saved to : {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
