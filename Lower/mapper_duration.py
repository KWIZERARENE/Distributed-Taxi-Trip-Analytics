#!/usr/bin/env python3
"""
mapper_duration.py
Key/value contract: duration bucket -> minutes
Buckets: 0-10, 10-20, 20-40, 40-60, 60+ minutes (Section 9.8).
"""
import sys
from datetime import datetime


def bucket_for(minutes):
    if minutes < 10:
        return "00-10min"
    if minutes < 20:
        return "10-20min"
    if minutes < 40:
        return "20-40min"
    if minutes < 60:
        return "40-60min"
    return "60min+"


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        fields = line.split(",")
        if len(fields) < 3:
            continue
        try:
            pickup = datetime.strptime(fields[1].strip(), "%Y-%m-%d %H:%M:%S")
            dropoff = datetime.strptime(fields[2].strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        minutes = (dropoff - pickup).total_seconds() / 60.0
        if minutes <= 0:
            continue
        print(f"{bucket_for(minutes)}\t{minutes:.4f}")


if __name__ == "__main__":
    main()
