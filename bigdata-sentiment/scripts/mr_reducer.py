#!/usr/bin/env python3
"""
Hadoop Streaming Reducer — Phase 2 of the cleaning pipeline.

Receives sorted key-value pairs from the mapper.
Key = md5 hash of cleaned comment text (identical comments → same key).
For each unique key, emits only the first record (deduplication).
Output is JSONL written to HDFS /project/cleaned_data/.

Run via Hadoop Streaming — do not run directly.
"""

import sys
import json

current_key = None

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue

    parts = line.split("\t", 1)
    if len(parts) != 2:
        continue

    key, value = parts
    if key == current_key:
        # Duplicate — skip
        continue

    current_key = key
    # Emit the record (without the key prefix) as plain JSON line
    try:
        record = json.loads(value)
        print(json.dumps(record, ensure_ascii=False))
    except json.JSONDecodeError:
        continue
