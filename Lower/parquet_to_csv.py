"""
parquet_to_csv.py

Converts NYC TLC monthly taxi trip Parquet files to CSV so they can be
uploaded to HDFS and read line-by-line by Hadoop Streaming mappers.

Reads each Parquet file in batches (via pyarrow) instead of loading the
whole file into memory at once, so it scales to multi-million-row months.

Run from a terminal (recommended):
    python parquet_to_csv.py --input-dir "C:\\Users\\user\\Desktop\\Bigdata" --output-dir "C:\\Users\\user\\Desktop\\Bigdata\\CSV"
    python parquet_to_csv.py --input-dir ./raw_parquet --output-dir ./raw_csv --batch-size 500000
"""

import argparse
import csv
import os
import sys
import time
from typing import Tuple

try:
    import pyarrow.parquet as pq
except ImportError:
    sys.exit("pyarrow is required. Install it with:\n    pip install pyarrow")

DEFAULT_INPUT_DIR = r"C:\Users\user\Desktop\Bigdata"
DEFAULT_OUTPUT_DIR = r"C:\Users\user\Desktop\Bigdata\CSV"
DEFAULT_BATCH_SIZE = 250_000


def convert_file(input_path: str, output_path: str, batch_size: int) -> Tuple[int, float]:
    """Stream one Parquet file to CSV in batches. Returns (row_count, seconds_taken)."""
    start = time.time()
    row_count = 0
    parquet_file = pq.ParquetFile(input_path)
    header_written = False

    with open(output_path, "w", newline="", encoding="utf-8") as out_f:
        writer = None
        for batch in parquet_file.iter_batches(batch_size=batch_size):
            table_dict = batch.to_pydict()
            columns = list(table_dict.keys())
            n_rows = len(next(iter(table_dict.values()))) if columns else 0

            if writer is None:
                writer = csv.writer(out_f)
            if not header_written:
                writer.writerow(columns)
                header_written = True

            for i in range(n_rows):
                writer.writerow([table_dict[col][i] for col in columns])
            row_count += n_rows

    elapsed = time.time() - start
    return row_count, elapsed


def convert_all(input_dir: str, output_dir: str, batch_size: int):
    if not os.path.isdir(input_dir):
        sys.exit(f"Input directory not found: {input_dir}")
    os.makedirs(output_dir, exist_ok=True)

    parquet_files = [e.name for e in sorted(os.scandir(input_dir), key=lambda e: e.name)
                      if e.name.lower().endswith(".parquet") and e.is_file()]
    if not parquet_files:
        sys.exit(f"No .parquet files found in {input_dir}")

    print(f"Found {len(parquet_files)} Parquet file(s) to convert.\n")
    summary = []
    for fname in parquet_files:
        in_path = os.path.join(input_dir, fname)
        out_path = os.path.join(output_dir, os.path.splitext(fname)[0] + ".csv")
        in_size_mb = os.path.getsize(in_path) / (1024 * 1024)
        print(f"Converting {fname} ({in_size_mb:.1f} MB)...")
        row_count, elapsed = convert_file(in_path, out_path, batch_size)
        out_size_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(f"  -> {os.path.basename(out_path)}: {row_count:,} rows, {out_size_mb:.1f} MB, {elapsed:.1f}s\n")
        summary.append({"file": fname, "rows": row_count, "parquet_mb": round(in_size_mb, 1),
                         "csv_mb": round(out_size_mb, 1), "seconds": round(elapsed, 1)})

    print("=" * 60)
    print("Conversion summary:")
    print("=" * 60)
    total_rows = total_parquet_mb = total_csv_mb = 0
    for s in summary:
        print(f"{s['file']:35s} rows={s['rows']:>12,}  parquet={s['parquet_mb']:>8.1f}MB  "
              f"csv={s['csv_mb']:>8.1f}MB  time={s['seconds']:>6.1f}s")
        total_rows += s["rows"]; total_parquet_mb += s["parquet_mb"]; total_csv_mb += s["csv_mb"]
    print("-" * 60)
    print(f"TOTAL rows: {total_rows:,}")
    print(f"TOTAL parquet size: {total_parquet_mb:.1f} MB")
    if total_parquet_mb > 0:
        print(f"TOTAL csv size: {total_csv_mb:.1f} MB  (growth factor: {total_csv_mb/total_parquet_mb:.2f}x)")


def main():
    if len(sys.argv) == 1:
        convert_all(DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_BATCH_SIZE)
        return
    parser = argparse.ArgumentParser(description="Convert TLC Parquet files to CSV.")
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--batch-size", type=int, default=250_000)
    args = parser.parse_args()
    convert_all(args.input_dir, args.output_dir, args.batch_size)


if __name__ == "__main__":
    main()
