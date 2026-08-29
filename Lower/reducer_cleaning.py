#!/usr/bin/env python3
"""
reducer_cleaning.py
Key/value contract: full raw record -> 1   =>   unique valid record (deduplicated)

Relies on Hadoop's guaranteed sort-by-key order during Shuffle & Sort:
identical records arrive consecutively, so duplicates are detected with a
single "accumulate while key matches, flush on change" pass with O(1) memory.
"""
import sys


def counter(group, name, amount=1):
    sys.stderr.write(f"reporter:counter:{group},{name},{amount}\n")


def main():
    current_record = None
    current_count = 0

    def flush(record, count):
        if record is None:
            return
        print(record)
        if count > 1:
            counter("Cleaning", "DUPLICATE_RECORDS", count - 1)

    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        record, _, _value = line.rpartition("\t")
        if record == current_record:
            current_count += 1
        else:
            flush(current_record, current_count)
            current_record = record
            current_count = 1

    flush(current_record, current_count)


if __name__ == "__main__":
    main()
