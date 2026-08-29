#!/usr/bin/env python
"""
reducer_cleaning.py

Deduplicates cleaned FHVHV trip records. Hadoop Streaming's Shuffle and Sort
stage groups all records sharing the same composite key (emitted by
mapper_cleaning.py) together and delivers them to the reducer in sorted key
order. For each key, only the FIRST record encountered is kept — any
additional records sharing that key are treated as exact/near-duplicate
trips and dropped.

Emits the cleaned, deduplicated CSV lines (key stripped) as the final
output, written to /taxi_project/input/cleaned.

Note: this catches exact duplicates on the composite key (license number,
pickup time, dropoff time, pickup/dropoff zone, distance). Near-duplicates
that differ slightly in one of these fields would not be caught — worth a
one-line caveat in your Data Cleaning report section.
"""

import sys

current_key = None

for line in sys.stdin:
    line = line.rstrip("\n")
    if not line:
        continue

    try:
        key, value = line.split("\t", 1)
    except ValueError:
        continue  # malformed line, skip defensively

    if key != current_key:
        # First time seeing this key in sorted order -> keep it
        current_key = key
        print(value)
        sys.stderr.write("reporter:counter:cleaning,unique_records_kept,1\n")
    else:
        # Same key as the previous record -> duplicate, drop it
        sys.stderr.write("reporter:counter:cleaning,dropped_duplicate,1\n")
