#!/usr/bin/env python3
"""
Scores every comment in the youtube_comments table using VADER.

VADER (Valence Aware Dictionary and sEntiment Reasoner) is well-suited
for short social media text — it handles slang, punctuation emphasis,
and emoji context better than TextBlob for this type of data.

Scoring:
  compound score > 0.05  → positive
  compound score < -0.05 → negative
  otherwise              → neutral

Run from your terminal:
    python3 scripts/sentiment_analysis.py
"""

import psycopg2
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

DB_PARAMS = dict(
    host="127.0.0.1",
    port=5432,
    dbname="sentiment_project",
    user="hex",
    password="hexpass",
)


def label(compound: float) -> str:
    if compound > 0.05:
        return "positive"
    if compound < -0.05:
        return "negative"
    return "neutral"


def main():
    analyzer = SentimentIntensityAnalyzer()

    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("SELECT id, comment_text FROM youtube_comments ORDER BY id;")
    rows = cur.fetchall()
    print(f"Scoring {len(rows)} comments with VADER...")

    updates = []
    for row_id, text in rows:
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]
        updates.append((compound, label(compound), row_id))

    cur.executemany(
        "UPDATE youtube_comments SET sentiment_score=%s, sentiment_label=%s WHERE id=%s",
        updates,
    )
    conn.commit()
    print(f"Updated {cur.rowcount} rows")

    # Quick distribution summary
    cur.execute("""
        SELECT sentiment_label, COUNT(*),
               ROUND(AVG(sentiment_score)::numeric, 3)
        FROM youtube_comments
        GROUP BY sentiment_label
        ORDER BY COUNT(*) DESC;
    """)
    print("\nSentiment distribution:")
    print(f"{'Label':<12} {'Count':>6}  {'Avg score':>10}")
    print("-" * 32)
    for lbl, count, avg in cur.fetchall():
        print(f"{lbl:<12} {count:>6}  {avg:>10}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
