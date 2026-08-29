#!/usr/bin/env python3
"""
reducer_route.py  (Multi-stage Workflow 2, Job 1)
Key/value contract: "PU-DO" route key -> 1  =>  route -> total trips
Output (routes.tsv) becomes the input to Job 2 (mapper_topn.py, reused).
"""
import sys


def main():
    current_route = None
    current_total = 0

    def flush(route, total):
        if route is not None:
            print(f"{route}\t{total}")

    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        route, _, value = line.partition("\t")
        if route == current_route:
            current_total += int(value)
        else:
            flush(current_route, current_total)
            current_route, current_total = route, int(value)

    flush(current_route, current_total)


if __name__ == "__main__":
    main()
