# 🍎 Apple YouTube Sentiment Analysis Pipeline

> A Big Data & Analytics university project that analyzes public perception of Apple products through YouTube comments using Python, VADER sentiment analysis, and PostgreSQL.

---

## 📊 Results

| Sentiment | Count | Percentage | Avg VADER Score |
|-----------|-------|------------|-----------------|
| ✅ Positive | 135 | 56.5% | +0.574 |
| ➖ Neutral | 85 | 35.6% | ~0.000 |
| ❌ Negative | 19 | 7.9% | -0.394 |

> **500** raw comments collected → **261** filtered (non-English) → **239** English comments analyzed

---

## 🔁 Pipeline Overview

```
YouTube Data API v3
        ↓
apple_youtube_comments.json   (500 raw comments)
        ↓
scripts/clean_comments.py     → filter English, strip URLs & special chars
        ↓
data/cleaned_comments.csv     (239 clean English comments)
        ↓
scripts/load_to_postgres.py   → auto-create DB + table, load all rows
        ↓
PostgreSQL: sentiment_db → youtube_comments
        ↓
scripts/sentiment_analysis.py → VADER scoring, update DB
        ↓
scripts/visualize.py          → generate 5 PNG charts
        ↓
visualizations/               → pie chart, bar chart, wordclouds, trend line
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10+ | All scripting |
| YouTube Data API v3 | Comment collection |
| `langdetect` | Filter non-English comments |
| `vaderSentiment` | Sentiment scoring |
| PostgreSQL 18 | Data storage & querying |
| `psycopg2` | Python ↔ PostgreSQL bridge |
| `pandas` | Data manipulation |
| `matplotlib` / `seaborn` | Charts |
| `wordcloud` | Word cloud images |
| `python-dotenv` | Load credentials from `.env` |

---

## ✅ Prerequisites

Before you start, make sure you have:

- **Python 3.10+** → check with `python --version`
- **PostgreSQL 18** installed and running → [download here](https://www.postgresql.org/download/)
- **YouTube Data API v3 key** → free from [Google Cloud Console](https://console.cloud.google.com)

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/youssef-880/bigdata-sentiment.git
cd bigdata-sentiment/bigdata-sentiment
```

> ⚠️ All commands from this point are run from inside the `bigdata-sentiment/bigdata-sentiment/` folder.

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Create your `.env` file

Create a file named `.env` in the `bigdata-sentiment/` folder (same level as `requirements.txt`).

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sentiment_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
```

**What each variable means:**

| Variable | What to enter |
|----------|--------------|
| `YOUTUBE_API_KEY` | Your API key from Google Cloud Console → APIs & Services → Credentials |
| `DB_HOST` | Leave as `localhost` |
| `DB_PORT` | Leave as `5432` (default PostgreSQL port) |
| `DB_NAME` | Leave as `sentiment_db` — created automatically |
| `DB_USER` | Your PostgreSQL username (usually `postgres`) |
| `DB_PASSWORD` | Your PostgreSQL password |

> 🔑 **How to get a YouTube API key:**
> 1. Go to [console.cloud.google.com](https://console.cloud.google.com)
> 2. Create or select a project
> 3. Go to **APIs & Services** → **Enable APIs** → search **YouTube Data API v3** → Enable
> 4. Go to **Credentials** → **Create Credentials** → **API Key**
> 5. Paste the key into your `.env`

> ⚠️ **Never commit your `.env` file to GitHub.**

---

### 4. Verify PostgreSQL is running

**Windows (PowerShell):**
```powershell
Get-Service -Name postgresql*
```
If it shows `Stopped`:
```powershell
Start-Service -Name postgresql-x64-18
```

**Linux/Mac:**
```bash
sudo service postgresql status
```

> You do **not** need to create the database manually — the load script creates `sentiment_db` automatically.

---

## ▶️ Running the Pipeline

### Step 1 — Clean the comments

```bash
python scripts/clean_comments.py
```

Reads the raw JSON, keeps only English comments, removes URLs and special characters, saves to CSV.

**Expected output:**
```
Total comments  : 500
Kept (English)  : 239
Filtered out    : 261
Output saved to : .../data/cleaned_comments.csv
```

---

### Step 2 — Load into PostgreSQL

```bash
python scripts/load_to_postgres.py
```

Creates the database and table if they don't exist, then loads all cleaned comments.

**Expected output:**
```
Loaded 239 records from cleaned_comments.csv
Created database: sentiment_db
Inserted 239 rows into youtube_comments
Table row count: 239
```

---

### Step 3 — Run VADER sentiment analysis

```bash
python scripts/sentiment_analysis.py
```

Scores every comment and writes the label and score back to the database.

**Scoring thresholds:**
- compound > `0.05` → **positive**
- compound < `-0.05` → **negative**
- between `-0.05` and `0.05` → **neutral**

**Expected output:**
```
Scoring 239 comments with VADER...
Updated 239 rows

Sentiment distribution:
Label         Count   Avg score
--------------------------------
positive        135       0.574
neutral          85       0.001
negative         19      -0.394
```

---

### Step 4 — Generate visualizations

```bash
python scripts/visualize.py
```

Saves 5 PNG files to `visualizations/`:

| File | Description |
|------|-------------|
| `sentiment_pie.png` | Pie chart of sentiment split |
| `sentiment_distribution.png` | Bar chart with percentages |
| `wordcloud_positive.png` | Most common words in positive comments |
| `wordcloud_negative.png` | Most common words in negative comments |
| `sentiment_over_time.png` | Monthly average sentiment trend |

---

### Step 5 — Run SQL analysis (optional)

**Windows:**
```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d sentiment_db -f sql/analysis.sql
```

**Linux/Mac:**
```bash
psql -U postgres -d sentiment_db -f sql/analysis.sql
```

Returns: sentiment distribution, top 10 most liked comments per sentiment, overall average score.

---

## 📁 Repository Structure

```
bigdata-sentiment/
│
├── bigdata-sentiment/
│   ├── .env                            ← your credentials (never commit)
│   ├── requirements.txt
│   │
│   ├── data/
│   │   ├── apple_youtube_comments.json ← 500 raw YouTube comments
│   │   └── cleaned_comments.csv        ← 239 English comments (generated)
│   │
│   ├── scripts/
│   │   ├── clean_comments.py           ← Step 1: filter + clean
│   │   ├── load_to_postgres.py         ← Step 2: CSV → PostgreSQL
│   │   ├── sentiment_analysis.py       ← Step 3: VADER scoring
│   │   ├── visualize.py                ← Step 4: generate charts
│   │   ├── collect_youtube_comments.py ← YouTube API data collection
│   │   ├── mr_mapper.py                ← Hadoop Streaming mapper
│   │   └── mr_reducer.py               ← Hadoop Streaming reducer
│   │
│   ├── sql/
│   │   ├── schema.sql                  ← table definition
│   │   ├── analysis.sql                ← 3 core queries
│   │   └── analysis_queries.sql        ← 10 extended queries
│   │
│   ├── visualizations/                 ← generated PNG charts
│   ├── notebooks/                      ← Jupyter notebooks
│   └── report/                         ← final report
│
└── README.md
```

---

## 🗄️ Database Schema

**Database:** `sentiment_db` | **Table:** `youtube_comments`

| Column | Type | Description |
|--------|------|-------------|
| `id` | SERIAL PK | Auto-increment ID |
| `video_id` | VARCHAR(20) | YouTube video ID |
| `video_title` | TEXT | Video title |
| `comment_text` | TEXT | Cleaned comment |
| `author` | VARCHAR(255) | YouTube username |
| `like_count` | INTEGER | Likes on comment |
| `published_at` | TIMESTAMPTZ | When comment was posted |
| `sentiment_score` | FLOAT | VADER compound score (-1.0 to +1.0) |
| `sentiment_label` | VARCHAR(10) | `positive` / `neutral` / `negative` |
| `created_at` | TIMESTAMPTZ | Row insert timestamp |

---

## 🔧 Troubleshooting

**`Could not open requirements file`**
```bash
# You're in the wrong folder — run this first:
cd bigdata-sentiment/bigdata-sentiment
```

**`password authentication failed for user "postgres"`**  
Your `DB_PASSWORD` in `.env` is wrong. Reset it on Windows (run PowerShell **as Administrator**):
```powershell
# 1. Disable password requirement temporarily
(Get-Content "C:\Program Files\PostgreSQL\18\data\pg_hba.conf") -replace "scram-sha-256", "trust" | Set-Content "C:\Program Files\PostgreSQL\18\data\pg_hba.conf"
Restart-Service postgresql-x64-18
Start-Sleep -Seconds 3

# 2. Set a new password (no prompt will appear)
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -c "ALTER USER postgres WITH PASSWORD 'yournewpassword';"

# 3. Re-enable password security
(Get-Content "C:\Program Files\PostgreSQL\18\data\pg_hba.conf") -replace "trust", "scram-sha-256" | Set-Content "C:\Program Files\PostgreSQL\18\data\pg_hba.conf"
Restart-Service postgresql-x64-18
```
Then update `DB_PASSWORD` in your `.env`.

**`Data file not found: cleaned_comments.csv`**
```bash
# Run Step 1 first:
python scripts/clean_comments.py
```

**`ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

---

## ⚠️ Known Limitations

- **VADER + slang:** VADER misclassifies informal positives as negative — *"this is fire"*, *"killing it"*, *"hell yeah"* all score negative because VADER uses a general dictionary not tuned for YouTube/tech slang.
- **Neutral = no sentiment words found:** A score of exactly 0.000 doesn't mean the comment is truly neutral — it means VADER found no recognized sentiment words.
- **langdetect is probabilistic:** Short or mixed-language comments can be misclassified.
- **Small dataset:** 500 comments from a limited set of videos — results are not broadly generalizable.

---

## 🤝 Contributing

```bash
# 1. Sync before starting
git checkout main
git pull origin main

# 2. Create your branch
git checkout -b yourname/what-youre-doing

# 3. Make changes and commit
git add .
git commit -m "Brief description of what you changed"

# 4. Push and open a Pull Request
git push origin yourname/what-youre-doing
```

> Never commit `.env`, credentials, or large raw data files to `main`.
