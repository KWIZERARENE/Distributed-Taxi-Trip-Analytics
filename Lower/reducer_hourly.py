#!/usr/bin/env python3
"""
reducer_hourly.py
Key/value contract: hour -> 1  =>  hour -> total trips
Standard "accumulate while key matches, flush on change" reducer, relying on
Hadoop Shuffle & Sort delivering keys (hours "00".."23") in sorted order.
"""
import sys


def main():
    current_hour = None
    current_total = 0

    def flush(hour, total):
        if hour is not None:
            print(f"{hour}\t{total}")

    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        hour, _, value = line.partition("\t")
        if hour == current_hour:
            current_total += int(value)
        else:
            flush(current_hour, current_total)
            current_hour, current_total = hour, int(value)

    flush(current_hour, current_total)


if __name__ == "__main__":
    main()
