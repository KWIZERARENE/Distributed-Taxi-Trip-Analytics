#!/usr/bin/env python3
"""
reducer_daily.py
Key/value contract: day name -> 1  =>  day -> total trips
"""
import sys


def main():
    current_day = None
    current_total = 0

    def flush(day, total):
        if day is not None:
            print(f"{day}\t{total}")

    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        day, _, value = line.partition("\t")
        if day == current_day:
            current_total += int(value)
        else:
            flush(current_day, current_total)
            current_day, current_total = day, int(value)

    flush(current_day, current_total)


if __name__ == "__main__":
    main()
