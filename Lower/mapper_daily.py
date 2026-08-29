#!/usr/bin/env python3
"""
mapper_daily.py
Key/value contract: day name ("Mon".."Sun") -> 1
Extracts the day-of-week from pickup_datetime (field index 1).
"""
import sys
from datetime import datetime

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        fields = line.split(",")
        if len(fields) < 2:
            continue
        try:
            dt = datetime.strptime(fields[1].strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        print(f"{DAY_NAMES[dt.weekday()]}\t1")


if __name__ == "__main__":
    main()
