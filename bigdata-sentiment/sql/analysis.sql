-- Apple YouTube Sentiment — Core Analysis Queries
-- Connect: psql -U postgres -d sentiment_db
-- Then run: \i sql/analysis.sql

-- 1. Overall sentiment distribution
SELECT
    sentiment_label,
    COUNT(*)                                                      AS comment_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)           AS pct
FROM youtube_comments
WHERE sentiment_label IS NOT NULL
GROUP BY sentiment_label
ORDER BY comment_count DESC;

-- 2. Top 10 most liked comments per sentiment
SELECT
    sentiment_label,
    author,
    like_count,
    ROUND(sentiment_score::numeric, 3)  AS score,
    LEFT(comment_text, 120)             AS comment_preview
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY sentiment_label ORDER BY like_count DESC) AS rn
    FROM youtube_comments
    WHERE sentiment_label IS NOT NULL
) ranked
WHERE rn <= 10
ORDER BY sentiment_label, like_count DESC;

-- 3. Average sentiment score overall
SELECT
    ROUND(AVG(sentiment_score)::numeric, 4)  AS avg_sentiment_score,
    MIN(sentiment_score)                      AS min_score,
    MAX(sentiment_score)                      AS max_score,
    COUNT(*)                                  AS total_scored
FROM youtube_comments
WHERE sentiment_score IS NOT NULL;
