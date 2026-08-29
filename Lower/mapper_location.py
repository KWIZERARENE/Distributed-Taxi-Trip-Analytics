#!/usr/bin/env python3
"""
mapper_location.py  (Multi-stage Workflow 1, Job 1)
Key/value contract: PUlocationID -> 1
"""
import sys


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        fields = line.split(",")
        if len(fields) < 4:
            continue
        pu_zone = fields[3].strip()
        if pu_zone:
            print(f"{pu_zone}\t1")


if __name__ == "__main__":
    main()
