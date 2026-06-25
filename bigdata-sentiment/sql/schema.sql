-- Apple YouTube Sentiment — Table Schema
-- Assumes you are already connected to sentiment_db.
-- load_to_postgres.py creates the database and runs this automatically.
-- Manual run: psql -U postgres -d sentiment_db -f sql/schema.sql

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
CREATE INDEX IF NOT EXISTS idx_published_at    ON youtube_comments(published_at);

SELECT 'Schema setup complete.' AS status;
