#!/usr/bin/env python3
"""
Hadoop Streaming Mapper — Phase 1 of the cleaning pipeline.

Reads one JSON comment per line from stdin (HDFS input).
Applies: English detection, URL stripping, emoji normalization,
         null-field handling.
Emits: hash_of_cleaned_text TAB cleaned_json  (so reducer can deduplicate)

Run via Hadoop Streaming — do not run directly.
"""

import sys
import json
import re
import hashlib
import unicodedata
from langdetect import detect, LangDetectException

EMOJI_PATTERN = re.compile(
    "[\U00010000-\U0010ffff"
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")


def clean_text(text: str) -> str:
    text = URL_PATTERN.sub(" ", text)
    text = EMOJI_PATTERN.sub(" ", text)
    # Normalise unicode (e.g. fancy quotes → ASCII)
    text = unicodedata.normalize("NFKC", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_english(text: str) -> bool:
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        raw_comment = record.get("comment", "")
        if not raw_comment or not raw_comment.strip():
            continue

        if not is_english(raw_comment):
            continue

        cleaned = clean_text(raw_comment)
        if not cleaned:
            continue

        # Build output record
        out = {
            "videoId":     record.get("videoId", ""),
            "videoTitle":  record.get("videoTitle", ""),
            "comment":     cleaned,
            "author":      record.get("author", ""),
            "likeCount":   record.get("likeCount", 0),
            "publishedAt": record.get("publishedAt", ""),
        }

        key = hashlib.md5(cleaned.lower().encode()).hexdigest()
        print(f"{key}\t{json.dumps(out, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
