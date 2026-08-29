#!/usr/bin/env python3
"""
mapper_cleaning.py
Key/value contract: full raw record (as-is) -> 1

Reads raw fhv_tripdata CSV lines from stdin, validates each record against
the rules in Section 6.1 of the report, and emits VALID records unchanged
(tab is not used as a delimiter here -- the whole comma-separated record is
the key) so the reducer can deduplicate via Hadoop's sorted-key guarantee.
Invalid records are dropped and counted via Hadoop Streaming counters
(stderr "reporter:counter:" protocol), never silently discarded.
"""
import sys
from datetime import datetime

EXPECTED_FIELDS = 7  # dispatching_base_num, pickup_datetime, dropOff_datetime,
                      # PUlocationID, DOlocationID, SR_Flag, Affiliated_base_number
UNKNOWN_ZONES = {"264", "265"}
MAX_DURATION_HOURS = 24


def counter(group, name, amount=1):
    sys.stderr.write(f"reporter:counter:{group},{name},{amount}\n")


def parse_dt(s):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except ValueError:
            continue
    return None


def main():
    header_skipped = False
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        if not header_skipped and line.lower().startswith("dispatching_base_num"):
            header_skipped = True
            continue

        fields = line.split(",")
        if len(fields) != EXPECTED_FIELDS:
            counter("Cleaning", "MALFORMED_ROW")
            continue

        base, pickup_s, dropoff_s, pu_zone, do_zone, sr_flag, aff_base = fields

        pickup_dt = parse_dt(pickup_s)
        dropoff_dt = parse_dt(dropoff_s)
        if pickup_dt is None or dropoff_dt is None:
            counter("Cleaning", "INVALID_TIMESTAMP")
            continue

        duration_seconds = (dropoff_dt - pickup_dt).total_seconds()
        if duration_seconds <= 0:
            counter("Cleaning", "NEGATIVE_OR_ZERO_DURATION")
            continue
        if duration_seconds > MAX_DURATION_HOURS * 3600:
            counter("Cleaning", "IMPOSSIBLE_DURATION_OVER_24H")
            continue

        # Missing location IDs and unknown zones are KEPT but flagged.
        if not pu_zone.strip() or not do_zone.strip():
            counter("Cleaning", "MISSING_LOCATION_ID")
        if pu_zone.strip() in UNKNOWN_ZONES or do_zone.strip() in UNKNOWN_ZONES:
            counter("Cleaning", "UNKNOWN_ZONE_264_265")

        counter("Cleaning", "VALID_RECORD")
        print(f"{line}\t1")


if __name__ == "__main__":
    main()
