#!/usr/bin/env python3
"""
Generates three visualizations from sentiment analysis results:
  1. sentiment_distribution.png  — bar chart of positive/negative/neutral counts
  2. wordcloud_positive.png       — word cloud of positive comment terms
  3. wordcloud_negative.png       — word cloud of negative comment terms
  4. sentiment_over_time.png      — monthly average compound score trend

Saves PNGs to visualizations/ directory.
Run from your terminal:
    python3 scripts/visualize.py
"""

import os
import re
import sys
from pathlib import Path
from collections import Counter

import psycopg2
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from wordcloud import WordCloud
from dotenv import load_dotenv
import nltk

load_dotenv()

# Download stopwords if needed
try:
    from nltk.corpus import stopwords
    STOP_WORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords
    STOP_WORDS = set(stopwords.words("english"))

# Common filler words that aren't useful in a word cloud
EXTRA_STOP = {"like", "im", "get", "one", "its", "got", "ur", "u", "it", "thats",
              "dont", "just", "yeah", "oh", "yes", "no", "ok", "lol", "haha",
              "iphone", "apple", "phone", "video"}
STOP_WORDS |= EXTRA_STOP

DB_PARAMS = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432)),
    dbname=os.getenv("DB_NAME", "sentiment_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
)

OUTPUT_DIR = Path(__file__).parent.parent / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {
    "positive": "#4CAF50",
    "neutral":  "#2196F3",
    "negative": "#F44336",
}


def connect():
    try:
        return psycopg2.connect(**DB_PARAMS)
    except psycopg2.OperationalError as e:
        sys.exit(f"DB connection failed: {e}\nRun: python3 scripts/load_to_postgres.py first")


def load_data(conn) -> pd.DataFrame:
    return pd.read_sql(
        """
        SELECT comment_text, sentiment_label, sentiment_score, published_at, like_count
        FROM youtube_comments
        WHERE sentiment_label IS NOT NULL
        ORDER BY published_at
        """,
        conn,
        parse_dates=["published_at"],
    )


def clean_tokens(text: str) -> list[str]:
    tokens = re.findall(r"\b[a-z]{3,}\b", text.lower())
    return [t for t in tokens if t not in STOP_WORDS]


# ── Chart 1: Sentiment pie chart ─────────────────────────────────────────────
def plot_pie(df: pd.DataFrame):
    counts = df["sentiment_label"].value_counts().reindex(
        ["positive", "neutral", "negative"], fill_value=0
    )
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        counts.values,
        labels=[l.capitalize() for l in counts.index],
        colors=[COLORS[l] for l in counts.index],
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    ax.set_title("Apple YouTube Comments — Sentiment Distribution", fontsize=14, pad=15)
    path = OUTPUT_DIR / "sentiment_pie.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


# ── Chart 2: Sentiment bar chart ──────────────────────────────────────────────
def plot_distribution(df: pd.DataFrame):
    counts = df["sentiment_label"].value_counts().reindex(
        ["positive", "neutral", "negative"], fill_value=0
    )
    pcts = (counts / counts.sum() * 100).round(1)

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(
        counts.index,
        counts.values,
        color=[COLORS[l] for l in counts.index],
        edgecolor="white",
        linewidth=0.8,
    )
    for bar, pct in zip(bars, pcts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{pct}%",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    ax.set_title("Apple YouTube Comments — Sentiment Distribution", fontsize=14, pad=15)
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Number of Comments")
    ax.set_ylim(0, counts.max() * 1.15)
    ax.spines[["top", "right"]].set_visible(False)

    path = OUTPUT_DIR / "sentiment_distribution.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


# ── Charts 2 & 3: Word clouds ─────────────────────────────────────────────────
def plot_wordcloud(df: pd.DataFrame, sentiment: str):
    subset = df[df["sentiment_label"] == sentiment]["comment_text"]
    if subset.empty:
        print(f"No {sentiment} comments — skipping word cloud")
        return

    all_tokens = []
    for text in subset:
        all_tokens.extend(clean_tokens(str(text)))

    freq = Counter(all_tokens)
    if not freq:
        print(f"No usable tokens for {sentiment} word cloud")
        return

    wc = WordCloud(
        width=900,
        height=500,
        background_color="white",
        colormap="Greens" if sentiment == "positive" else "Reds",
        max_words=80,
        collocations=False,
    ).generate_from_frequencies(freq)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(
        f"Word Cloud — {sentiment.capitalize()} Comments",
        fontsize=14, pad=12,
    )

    path = OUTPUT_DIR / f"wordcloud_{sentiment}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


# ── Chart 4: Sentiment over time ──────────────────────────────────────────────
def plot_sentiment_over_time(df: pd.DataFrame):
    ts = df.dropna(subset=["published_at"]).copy()
    if ts.empty or ts["published_at"].nunique() < 3:
        print("Not enough time variation for trend chart — skipping")
        return

    ts["month"] = ts["published_at"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        ts.groupby("month")["sentiment_score"]
        .agg(["mean", "count"])
        .reset_index()
    )
    monthly.columns = ["month", "avg_score", "count"]

    # Only plot months with enough data
    monthly = monthly[monthly["count"] >= 3]
    if len(monthly) < 2:
        print("Too few months with data — skipping trend chart")
        return

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(
        monthly["month"],
        monthly["avg_score"],
        marker="o",
        color="#1565C0",
        linewidth=2,
        label="Avg Sentiment Score",
    )
    ax1.axhline(0, color="grey", linestyle="--", linewidth=0.8)
    ax1.fill_between(
        monthly["month"],
        monthly["avg_score"],
        0,
        where=monthly["avg_score"] >= 0,
        alpha=0.15,
        color="#4CAF50",
    )
    ax1.fill_between(
        monthly["month"],
        monthly["avg_score"],
        0,
        where=monthly["avg_score"] < 0,
        alpha=0.15,
        color="#F44336",
    )

    ax2 = ax1.twinx()
    ax2.bar(
        monthly["month"],
        monthly["count"],
        width=20,
        alpha=0.25,
        color="grey",
        label="Comment count",
    )
    ax2.set_ylabel("Comment Count", color="grey")

    ax1.set_title("Apple YouTube Sentiment Over Time (Monthly)", fontsize=14, pad=12)
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Average VADER Compound Score")
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate(rotation=30)
    ax1.spines[["top"]].set_visible(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    path = OUTPUT_DIR / "sentiment_over_time.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def main():
    conn = connect()
    df = load_data(conn)
    conn.close()

    print(f"Loaded {len(df)} rows for visualisation")
    print(df["sentiment_label"].value_counts().to_string())
    print()

    plot_pie(df)
    plot_distribution(df)
    plot_wordcloud(df, "positive")
    plot_wordcloud(df, "negative")
    plot_sentiment_over_time(df)
    print("\nAll visualizations saved to visualizations/")


if __name__ == "__main__":
    main()
