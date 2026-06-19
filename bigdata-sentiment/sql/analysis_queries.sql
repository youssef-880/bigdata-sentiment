-- Apple YouTube Sentiment — SQL Analysis Queries
-- Connect: psql -h 127.0.0.1 -U hex -d sentiment_project
-- Or:      psql -U hex -d sentiment_project  (if peer auth)

-- 1. Overall sentiment distribution
SELECT
    sentiment_label,
    COUNT(*) AS comment_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM youtube_comments
WHERE sentiment_label IS NOT NULL
GROUP BY sentiment_label
ORDER BY comment_count DESC;

-- 2. Average sentiment score per video
SELECT
    video_title,
    COUNT(*)                         AS total_comments,
    ROUND(AVG(sentiment_score)::numeric, 3) AS avg_sentiment,
    SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) AS positive,
    SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) AS negative,
    SUM(CASE WHEN sentiment_label = 'neutral'  THEN 1 ELSE 0 END) AS neutral
FROM youtube_comments
GROUP BY video_title
ORDER BY avg_sentiment DESC;

-- 3. Most-liked comments (top 10)
SELECT
    author,
    like_count,
    sentiment_label,
    ROUND(sentiment_score::numeric, 3) AS score,
    LEFT(comment_text, 120)            AS comment_preview
FROM youtube_comments
ORDER BY like_count DESC
LIMIT 10;

-- 4. Most-liked positive comments
SELECT
    author,
    like_count,
    ROUND(sentiment_score::numeric, 3) AS score,
    LEFT(comment_text, 120)            AS comment_preview
FROM youtube_comments
WHERE sentiment_label = 'positive'
ORDER BY like_count DESC
LIMIT 5;

-- 5. Most-liked negative comments
SELECT
    author,
    like_count,
    ROUND(sentiment_score::numeric, 3) AS score,
    LEFT(comment_text, 120)            AS comment_preview
FROM youtube_comments
WHERE sentiment_label = 'negative'
ORDER BY like_count DESC
LIMIT 5;

-- 6. Comment volume by video
SELECT
    video_id,
    video_title,
    COUNT(*) AS comment_count
FROM youtube_comments
GROUP BY video_id, video_title
ORDER BY comment_count DESC;

-- 7. Monthly sentiment trend (if data spans multiple months)
SELECT
    TO_CHAR(DATE_TRUNC('month', published_at), 'YYYY-MM') AS month,
    COUNT(*) AS total,
    ROUND(AVG(sentiment_score)::numeric, 3)               AS avg_score,
    SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) AS positive,
    SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) AS negative
FROM youtube_comments
WHERE published_at IS NOT NULL
GROUP BY DATE_TRUNC('month', published_at)
ORDER BY month;

-- 8. Sentiment by hour of day (engagement patterns)
SELECT
    EXTRACT(HOUR FROM published_at) AS hour_of_day,
    COUNT(*) AS comments,
    ROUND(AVG(sentiment_score)::numeric, 3) AS avg_sentiment
FROM youtube_comments
WHERE published_at IS NOT NULL
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- 9. Authors with most comments
SELECT
    author,
    COUNT(*) AS comments,
    ROUND(AVG(sentiment_score)::numeric, 3) AS avg_sentiment
FROM youtube_comments
GROUP BY author
HAVING COUNT(*) > 1
ORDER BY comments DESC
LIMIT 10;

-- 10. Top highly-engaged positive sentiment comments
SELECT
    video_title,
    author,
    like_count,
    ROUND(sentiment_score::numeric, 3) AS score,
    LEFT(comment_text, 100) AS comment_preview
FROM youtube_comments
WHERE sentiment_score > 0.5
ORDER BY like_count DESC
LIMIT 10;
