#!/usr/bin/env python3
"""
reducer_topn.py  (Multi-stage Workflow 1, Job 2)
Key/value contract: "ALL" -> (zone, count)  =>  ranked Top 10 / Bottom 10 zones

Because every value lands on this single reducer (key "ALL"), the reducer
must hold all (zone, count) pairs in memory -- this is only feasible because
Job 1 already aggregated raw trips down to ~260 TLC zones.
"""
import sys

TOP_N = 10
BOTTOM_N = 10


def main():
    pairs = []
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        _key, _, item = line.partition("\t")
        zone, _, count = item.partition("=")
        try:
            pairs.append((zone, int(count)))
        except ValueError:
            continue

    pairs.sort(key=lambda p: p[1], reverse=True)

    print("== TOP 10 ==")
    for zone, count in pairs[:TOP_N]:
        print(f"{zone}\t{count}")

    print("== BOTTOM 10 ==")
    for zone, count in sorted(pairs, key=lambda p: p[1])[:BOTTOM_N]:
        print(f"{zone}\t{count}")


if __name__ == "__main__":
    main()
