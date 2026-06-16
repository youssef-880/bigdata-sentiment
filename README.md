# Big Data & Analytics 

Sentiment analysis project tracking public perception of [Brand Name] across social media, using Hadoop, PostgreSQL, and Python for the Big Data & Analytics course.

## Project Pipeline
1. **Data Collection** – YouTube Data API v3 (comments on brand-related videos)
2. **Storage** – Hadoop / HDFS
3. **Cleaning** – MapReduce / Python preprocessing
4. **Analysis** – PostgreSQL + Python (VADER/TextBlob sentiment scoring)
5. **Visualization** – Tableau or Python (matplotlib/seaborn/wordcloud)
6. **Reporting** – Final report + presentation

## Repository Structure
```
├── data/               # Raw and cleaned datasets (gitignored if large)
├── scripts/            # Python scripts (collection, cleaning, sentiment)
├── notebooks/          # Jupyter notebooks for exploration/analysis
├── sql/                # SQL queries used for analysis
├── visualizations/     # Exported charts, dashboards, screenshots
├── report/             # Final report drafts
└── README.md
```

## Setup

Clone the repo:
```bash
git clone https://github.com/youssef-880/bigdata-sentiment.git
cd bigdata-sentiment
```

Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

Create a `.env` file in the root (never commit this) with your own API key:
```
YOUTUBE_API_KEY=your_key_here
```

## How to Submit Changes

We use a simple branch → pull request → merge workflow so we don't overwrite each other's work.

**1. Pull the latest changes before starting anything new:**
```bash
git checkout main
git pull origin main
```

**2. Create a new branch for your task** (don't work directly on `main`):
```bash
git checkout -b your-name/short-task-description
# example: git checkout -b alex/sentiment-script
```

**3. Make your changes, then stage and commit them:**
```bash
git add .
git commit -m "Add sentiment scoring script using VADER"
```
Write commit messages that describe *what* changed, not just "update" or "fix."

**4. Push your branch to GitHub:**
```bash
git push origin your-name/short-task-description
```

**5. Open a Pull Request (PR):**
- Go to the repo on GitHub — it'll show a banner to "Compare & pull request"
- Add a short description of what you did
- Tag a teammate to review if possible

**6. Review and merge:**
- At least one other group member should look it over before merging
- Once approved, click "Merge pull request" on GitHub
- Delete the branch after merging to keep things tidy

**7. Everyone re-syncs:**
```bash
git checkout main
git pull origin main
```

## Notes
- Never commit API keys, `.env` files, or large raw data dumps — add them to `.gitignore`.
- If you hit a merge conflict, don't panic: pull `main` into your branch, resolve the conflicting lines manually in the file, then commit and push again.

