#!/usr/bin/env python3
"""
reducer_duration.py
Key/value contract: bucket -> minutes  =>  bucket -> (count, average minutes)
"""
import sys


def main():
    current_bucket = None
    count = 0
    total_minutes = 0.0

    def flush(bucket, count, total_minutes):
        if bucket is not None and count > 0:
            print(f"{bucket}\t{count}\t{total_minutes / count:.2f}")

    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        bucket, _, value = line.partition("\t")
        minutes = float(value)
        if bucket == current_bucket:
            count += 1
            total_minutes += minutes
        else:
            flush(current_bucket, count, total_minutes)
            current_bucket, count, total_minutes = bucket, 1, minutes

    flush(current_bucket, count, total_minutes)


if __name__ == "__main__":
    main()
