#!/usr/bin/env python3
"""
reducer_route_topn.py  (Multi-stage Workflow 2, Job 2)
Key/value contract: "ALL" -> (route, count)  =>  ranked Top 20 routes

Paired with the same mapper_topn.py used for zone ranking (Section 9.3),
demonstrating the generic mapper is reusable across any (key,count) input.
"""
import sys

TOP_N = 20


def main():
    pairs = []
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        _key, _, item = line.partition("\t")
        route, _, count = item.partition("=")
        try:
            pairs.append((route, int(count)))
        except ValueError:
            continue

    pairs.sort(key=lambda p: p[1], reverse=True)
    for route, count in pairs[:TOP_N]:
        print(f"{route}\t{count}")


if __name__ == "__main__":
    main()
