-- Schema for the Apple YouTube sentiment project
-- Run as: sudo -u postgres psql -f sql/schema.sql

-- 1. Ensure the hex role exists with the password Python scripts use
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'hex') THEN
        CREATE USER hex WITH SUPERUSER PASSWORD 'hexpass';
    ELSE
        ALTER USER hex WITH PASSWORD 'hexpass';
    END IF;
END
$$;

-- 2. Create database (must be outside a transaction block — run manually if needed)
--    Uncomment and run if sentiment_project doesn't exist yet:
-- CREATE DATABASE sentiment_project OWNER hex;

\c sentiment_project

GRANT ALL PRIVILEGES ON DATABASE sentiment_project TO hex;

-- 3. Create the comments table
DROP TABLE IF EXISTS youtube_comments;

CREATE TABLE youtube_comments (
    id              SERIAL PRIMARY KEY,
    video_id        VARCHAR(20)  NOT NULL,
    video_title     TEXT,
    comment_text    TEXT         NOT NULL,
    author          VARCHAR(255),
    like_count      INTEGER      DEFAULT 0,
    published_at    TIMESTAMPTZ,
    sentiment_score FLOAT,
    sentiment_label VARCHAR(10),  -- 'positive', 'negative', 'neutral'
    created_at      TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX idx_sentiment_label ON youtube_comments(sentiment_label);
CREATE INDEX idx_video_id        ON youtube_comments(video_id);
CREATE INDEX idx_published_at    ON youtube_comments(published_at);

\dt
\d youtube_comments

SELECT 'Schema setup complete.' AS status;
