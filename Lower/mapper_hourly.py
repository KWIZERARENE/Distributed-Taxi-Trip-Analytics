#!/usr/bin/env python3
"""
mapper_hourly.py
Key/value contract: hour of day ("00".."23") -> 1
Extracts the hour from pickup_datetime (field index 1) of each cleaned record.
"""
import sys


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        fields = line.split(",")
        if len(fields) < 2:
            continue
        pickup = fields[1].strip()
        try:
            hour = pickup.split(" ")[1].split(":")[0].zfill(2)
        except IndexError:
            continue
        print(f"{hour}\t1")


if __name__ == "__main__":
    main()
