#!/usr/bin/env python3
"""
mapper_topn.py  (Multi-stage Workflow 1 & 2, Job 2 -- reused unchanged)
Key/value contract: constant key "ALL" -> (original_key, count)

Generic "funnel everything to one reducer for global ranking" mapper.
Input is any prior job's "key<TAB>count" output (locations or routes).
Because every record is sent to the single key "ALL", all (key, count)
pairs land on one reducer, which can then sort them globally.
"""
import sys


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        key, _, count = line.partition("\t")
        if not count:
            continue
        print(f"ALL\t{key}={count}")


if __name__ == "__main__":
    main()
