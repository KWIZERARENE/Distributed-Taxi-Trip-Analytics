#!/usr/bin/env python3
"""
reducer_anomaly.py
Key/value contract: anomaly type -> 1  =>  anomaly type -> total flagged records
Matches the exact observed output:
  MISSING_BASE_NUMBER            141700
  SAME_PICKUP_DROPOFF_ZONE        17527
  TOTAL_RECORDS_SCANNED          1939311
  VERY_LONG_TRIP_OVER_3H            5069
  VERY_SHORT_TRIP_UNDER_1MIN        6265
"""
import sys


def main():
    current_key = None
    current_total = 0

    def flush(key, total):
        if key is not None:
            print(f"{key}\t{total}")

    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        key, _, value = line.partition("\t")
        if key == current_key:
            current_total += int(value)
        else:
            flush(current_key, current_total)
            current_key, current_total = key, int(value)

    flush(current_key, current_total)


if __name__ == "__main__":
    main()
