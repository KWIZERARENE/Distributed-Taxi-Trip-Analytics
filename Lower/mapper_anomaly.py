#!/usr/bin/env python3
"""
mapper_anomaly.py
Key/value contract: anomaly type -> 1
Flags structurally-valid-but-suspicious records that survived cleaning
(Section 9.9). Counter names match the actual reducer output observed:
  MISSING_BASE_NUMBER, SAME_PICKUP_DROPOFF_ZONE,
  VERY_LONG_TRIP_OVER_3H, VERY_SHORT_TRIP_UNDER_1MIN
Categories are not mutually exclusive -- a single record can emit more
than one anomaly key.
"""
import sys
from datetime import datetime


def main():
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue
        fields = line.split(",")
        if len(fields) < 7:
            continue
        base, pickup_s, dropoff_s, pu_zone, do_zone, sr_flag, aff_base = fields

        print("TOTAL_RECORDS_SCANNED\t1")

        if not base.strip() and not aff_base.strip():
            print("MISSING_BASE_NUMBER\t1")

        if pu_zone.strip() and pu_zone.strip() == do_zone.strip():
            print("SAME_PICKUP_DROPOFF_ZONE\t1")

        try:
            pickup = datetime.strptime(pickup_s.strip(), "%Y-%m-%d %H:%M:%S")
            dropoff = datetime.strptime(dropoff_s.strip(), "%Y-%m-%d %H:%M:%S")
            minutes = (dropoff - pickup).total_seconds() / 60.0
            if minutes > 180:
                print("VERY_LONG_TRIP_OVER_3H\t1")
            if minutes < 1:
                print("VERY_SHORT_TRIP_UNDER_1MIN\t1")
        except ValueError:
            continue


if __name__ == "__main__":
    main()
