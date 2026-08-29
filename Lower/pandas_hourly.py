#!/usr/bin/env python3
"""
pandas_hourly.py
Single-machine equivalent of the hourly-demand MapReduce job, used for the
Section 12 performance comparison.

CHANGED to combine multiple months: accepts either
  - a single CSV path, OR
  - a FOLDER of CSVs (all matching files are concatenated), OR
  - an explicit list of CSV paths on the command line.
This mirrors the Hadoop side, where combining months only required
pointing -input at a folder instead of one file.

Usage:
    python pandas_hourly.py "C:\\path\\to\\fhv_tripdata_2026-01.csv"
    python pandas_hourly.py "C:\\Users\\user\\Desktop\\Bigdata\\CSV"
    python pandas_hourly.py file1.csv file2.csv file3.csv file4.csv
"""
import glob
import os
import sys
import time

import pandas as pd
import psutil


def resolve_csv_paths(args):
    """Expand args (files and/or folders) into a sorted list of CSV paths."""
    paths = []
    for arg in args:
        if os.path.isdir(arg):
            paths.extend(sorted(glob.glob(os.path.join(arg, "*.csv"))))
        else:
            paths.append(arg)
    if not paths:
        sys.exit(f"No CSV files found for input(s): {args}")
    return paths


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python pandas_hourly.py <csv_or_folder> [more paths...]")

    csv_paths = resolve_csv_paths(sys.argv[1:])
    print(f"Reading {len(csv_paths)} file(s):")
    for p in csv_paths:
        print(f"  - {p}")
    print()

    process = psutil.Process()
    mem_before = process.memory_info().rss
    start = time.time()

    # Combine all months into one DataFrame, same as the Hadoop side combines
    # all files under one -input folder.
    frames = [
        pd.read_csv(p, usecols=["pickup_datetime"], parse_dates=["pickup_datetime"])
        for p in csv_paths
    ]
    df = pd.concat(frames, ignore_index=True)
    del frames

    df["hour"] = df["pickup_datetime"].dt.strftime("%H")
    hourly_counts = df.groupby("hour").size()

    elapsed = time.time() - start
    mem_after = process.memory_info().rss

    print("=== Hourly trip counts (Pandas, combined months) ===")
    print(hourly_counts.to_string())
    print()
    print(f"Total records processed: {len(df):,}")
    print(f"Execution time: {elapsed:.2f} seconds")
    print(f"Memory used: ~{(mem_after - mem_before) / (1024*1024):.1f} MB (delta), "
          f"{mem_after / (1024*1024):.1f} MB (peak process RSS)")


if __name__ == "__main__":
    main()
