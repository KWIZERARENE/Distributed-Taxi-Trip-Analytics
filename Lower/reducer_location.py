#!/usr/bin/env python3
"""
reducer_location.py  (Multi-stage Workflow 1, Job 1)
Key/value contract: PUlocationID -> 1  =>  zone -> total trips
Output of this job becomes the *input* to Job 2 (mapper_topn.py), forming
the compulsory two-stage MapReduce workflow described in Section 10.1.
"""
import sys


def main():
    current_zone = None
    current_total = 0

    def flush(zone, total):
        if zone is not None:
            print(f"{zone}\t{total}")

    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        zone, _, value = line.partition("\t")
        if zone == current_zone:
            current_total += int(value)
        else:
            flush(current_zone, current_total)
            current_zone, current_total = zone, int(value)

    flush(current_zone, current_total)


if __name__ == "__main__":
    main()
