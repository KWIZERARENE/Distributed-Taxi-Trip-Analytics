#!/usr/bin/env python3
"""
mapper_route.py  (Multi-stage Workflow 2, Job 1)
Key/value contract: "PUlocationID-DOlocationID" route key -> 1
"""
import sys


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        fields = line.split(",")
        if len(fields) < 5:
            continue
        pu_zone, do_zone = fields[3].strip(), fields[4].strip()
        if pu_zone and do_zone:
            print(f"{pu_zone}-{do_zone}\t1")


if __name__ == "__main__":
    main()
