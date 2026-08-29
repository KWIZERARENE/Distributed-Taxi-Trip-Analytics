#!/usr/bin/env python
"""
mapper_cleaning.py

Data-cleaning mapper for the FHVHV (High Volume For-Hire Vehicle) taxi trip
dataset. Reads raw CSV lines from /taxi_project/input/raw, validates each
record against a set of rules, and emits only VALID records as key\tvalue
pairs so the reducer stage can detect and drop exact duplicate trips during
Shuffle and Sort.

FHVHV schema (confirmed directly from this dataset's own CSV header, which
includes the newer cbd_congestion_fee column added for NYC congestion
pricing - not present in older versions of the TLC data dictionary):
hvfhs_license_num,dispatching_base_num,originating_base_num,request_datetime,
on_scene_datetime,pickup_datetime,dropoff_datetime,PULocationID,DOLocationID,
trip_miles,trip_time,base_passenger_fare,tolls,bcf,sales_tax,
congestion_surcharge,airport_fee,tips,driver_pay,shared_request_flag,
shared_match_flag,access_a_ride_flag,wav_request_flag,wav_match_flag,
cbd_congestion_fee

ADAPTATION NOTE (document this in your report's Data Cleaning section):
FHVHV has no passenger_count or payment_type field, unlike Yellow/Green taxi
data. Those two specific cleaning rules from the assignment brief therefore
do not apply to this dataset and are intentionally omitted here. All other
required cleaning categories (missing values, invalid timestamps,
zero/negative distance, invalid fares, impossible durations, duplicates,
invalid location IDs) are implemented below.

Invalid-record counts are reported via Hadoop counters (stderr
"reporter:counter:" lines). These appear in the YARN application UI and in
the job's final counters output — use them directly for your cleaning
report's "number and percentage of affected records" requirement.

Output format for valid records:
    <composite_key>\t<original_csv_line>
"""

import sys
import csv
from datetime import datetime

# Column indices (0-based) for the first 19 data fields.
# The final 5 columns (shared_request_flag ... wav_match_flag) are flags we
# don't validate individually, but they must still be present for the row
# to have the correct total field count.
COL = {
    "hvfhs_license_num": 0,
    "dispatching_base_num": 1,
    "originating_base_num": 2,
    "request_datetime": 3,
    "on_scene_datetime": 4,
    "pickup_datetime": 5,
    "dropoff_datetime": 6,
    "PULocationID": 7,
    "DOLocationID": 8,
    "trip_miles": 9,
    "trip_time": 10,
    "base_passenger_fare": 11,
    "tolls": 12,
    "bcf": 13,
    "sales_tax": 14,
    "congestion_surcharge": 15,
    "airport_fee": 16,
    "tips": 17,
    "driver_pay": 18,
}

EXPECTED_FIELD_COUNT = 25  # 19 data columns + 5 trailing flag columns + cbd_congestion_fee

MAX_TRIP_SECONDS = 24 * 60 * 60  # trips longer than this are invalid, not just anomalous
MIN_VALID_ZONE_ID = 1
MAX_VALID_ZONE_ID = 265  # NYC taxi zone ID range


def counter(group, name, amount=1):
    """Emit a Hadoop Streaming counter increment to stderr."""
    sys.stderr.write(f"reporter:counter:{group},{name},{amount}\n")


def parse_datetime(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def is_valid_row(fields):
    """Returns (is_valid: bool, reason: str or None)."""
    if len(fields) != EXPECTED_FIELD_COUNT:
        return False, "wrong_field_count"

    # --- Missing values on required fields ---
    required = [
        "hvfhs_license_num", "pickup_datetime", "dropoff_datetime",
        "PULocationID", "DOLocationID", "trip_miles", "trip_time",
        "base_passenger_fare",
    ]
    for field in required:
        idx = COL[field]
        if fields[idx] is None or fields[idx].strip() == "":
            return False, "missing_value"

    # --- Invalid timestamps ---
    pickup_dt = parse_datetime(fields[COL["pickup_datetime"]])
    dropoff_dt = parse_datetime(fields[COL["dropoff_datetime"]])
    if pickup_dt is None or dropoff_dt is None:
        return False, "invalid_timestamp"
    if dropoff_dt <= pickup_dt:
        return False, "invalid_timestamp"

    # --- Zero/negative distance ---
    try:
        trip_miles = float(fields[COL["trip_miles"]])
    except ValueError:
        return False, "invalid_distance"
    if trip_miles <= 0:
        return False, "invalid_distance"

    # --- Invalid / impossible trip duration ---
    try:
        trip_time = int(float(fields[COL["trip_time"]]))
    except ValueError:
        return False, "invalid_duration"
    if trip_time <= 0 or trip_time > MAX_TRIP_SECONDS:
        return False, "invalid_duration"

    # --- Invalid fares ---
    try:
        fare = float(fields[COL["base_passenger_fare"]])
    except ValueError:
        return False, "invalid_fare"
    if fare < 0:
        return False, "invalid_fare"

    # --- Invalid location IDs ---
    try:
        pu_id = int(float(fields[COL["PULocationID"]]))
        do_id = int(float(fields[COL["DOLocationID"]]))
    except ValueError:
        return False, "invalid_location"
    if not (MIN_VALID_ZONE_ID <= pu_id <= MAX_VALID_ZONE_ID):
        return False, "invalid_location"
    if not (MIN_VALID_ZONE_ID <= do_id <= MAX_VALID_ZONE_ID):
        return False, "invalid_location"

    return True, None


def main():
    reader = csv.reader(sys.stdin)
    for fields in reader:
        if not fields:
            continue

        # Skip header line(s) - can appear at the top of every uploaded file
        if fields[0] == "hvfhs_license_num":
            continue

        line_joined = ",".join(fields)
        if line_joined.strip() == "":
            continue

        counter("cleaning", "total_records_seen")

        valid, reason = is_valid_row(fields)
        if not valid:
            counter("cleaning", f"dropped_{reason}")
            continue

        # Composite key used by the reducer to detect exact-duplicate trips
        key = "|".join([
            fields[COL["hvfhs_license_num"]],
            fields[COL["pickup_datetime"]],
            fields[COL["dropoff_datetime"]],
            fields[COL["PULocationID"]],
            fields[COL["DOLocationID"]],
            fields[COL["trip_miles"]],
        ])

        counter("cleaning", "valid_records")
        print(f"{key}\t{line_joined}")


if __name__ == "__main__":
    main()