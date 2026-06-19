#!/bin/bash
# Master pipeline runner. Run from the repo root:
#   bash scripts/run_pipeline.sh
#
# Step 1 (DB setup) uses sudo and will prompt for your Linux password once.
# Steps 2-5 run as the hex user via the venv.

set -e
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON=/home/hex/venv/bin/python3

echo "============================================"
echo "  Apple YouTube Sentiment Pipeline"
echo "============================================"

# ── Step 0: Verify HDFS is running ───────────────────────────────────────────
echo ""
echo "=== Step 0: Checking HDFS ==="
if ! jps | grep -q NameNode; then
    echo "HDFS not running — starting..."
    start-dfs.sh
    sleep 3
fi
echo "HDFS OK: $(jps | grep -E 'NameNode|DataNode')"

# ── Step 1: Database setup ───────────────────────────────────────────────────
echo ""
echo "=== Step 1: PostgreSQL setup (requires sudo) ==="
sudo -u postgres psql -f "$REPO_DIR/sql/schema.sql"

# ── Step 2: MapReduce cleaning ───────────────────────────────────────────────
echo ""
echo "=== Step 2: Hadoop Streaming MapReduce cleaning ==="
bash "$REPO_DIR/scripts/run_mapreduce.sh"

# ── Step 3: Load into PostgreSQL ────────────────────────────────────────────
echo ""
echo "=== Step 3: Loading cleaned data into PostgreSQL ==="
$PYTHON "$REPO_DIR/scripts/load_to_postgres.py"

# ── Step 4: Sentiment analysis ───────────────────────────────────────────────
echo ""
echo "=== Step 4: VADER sentiment analysis ==="
$PYTHON "$REPO_DIR/scripts/sentiment_analysis.py"

# ── Step 5: Visualizations ───────────────────────────────────────────────────
echo ""
echo "=== Step 5: Generating visualizations ==="
$PYTHON "$REPO_DIR/scripts/visualize.py"

echo ""
echo "============================================"
echo "  Pipeline complete!"
echo "  Visualizations: $REPO_DIR/visualizations/"
echo "  DB:             psql -h 127.0.0.1 -U hex -d sentiment_project"
echo "  SQL analysis:   psql -h 127.0.0.1 -U hex -d sentiment_project -f sql/analysis_queries.sql"
echo "============================================"
