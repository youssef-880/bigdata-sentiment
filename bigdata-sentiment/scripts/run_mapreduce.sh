#!/bin/bash
# Runs the Hadoop Streaming MapReduce cleaning job.
# Input:  HDFS /project/raw_data/apple_youtube_comments.jsonl
# Output: HDFS /project/cleaned_data/  +  local data/cleaned_comments.jsonl

set -e
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STREAMING_JAR=/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar
PYTHON=/home/hex/venv/bin/python3
MAPPER="$REPO_DIR/scripts/mr_mapper.py"
REDUCER="$REPO_DIR/scripts/mr_reducer.py"

echo "=== MapReduce Cleaning Job ==="
echo "Input:  /project/raw_data/apple_youtube_comments.jsonl"
echo "Output: /project/cleaned_data/"

# Remove old output if present
hdfs dfs -rm -r /project/cleaned_data 2>/dev/null || true

hadoop jar "$STREAMING_JAR" \
  -files "$MAPPER,$REDUCER" \
  -mapper "$PYTHON mr_mapper.py" \
  -reducer "$PYTHON mr_reducer.py" \
  -input  /project/raw_data/apple_youtube_comments.jsonl \
  -output /project/cleaned_data/

echo ""
echo "=== HDFS Output ==="
hdfs dfs -ls /project/cleaned_data/

echo ""
echo "=== Downloading to local data/ ==="
hdfs dfs -get /project/cleaned_data/part-00000 "$REPO_DIR/data/cleaned_comments.jsonl"
echo "Lines in cleaned file: $(wc -l < "$REPO_DIR/data/cleaned_comments.jsonl")"
echo "Done."
