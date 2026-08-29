

import argparse
import csv
import os
import sys
import time
from typing import Tuple

try:
    import pyarrow.parquet as pq
except ImportError:
    sys.exit(
        "pyarrow is required. Install it with:\n"
        "    pip install pyarrow"
    )


# Used only as a fallback if you run this via VS Code's "Run" button
# without passing command-line arguments.
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

            # Transpose column-oriented dict into row-oriented tuples
            for i in range(n_rows):
                writer.writerow([table_dict[col][i] for col in columns])

            row_count += n_rows

    elapsed = time.time() - start
    return row_count, elapsed


def convert_all(input_dir: str, output_dir: str, batch_size: int):
    if not os.path.isdir(input_dir):
        sys.exit(f"Input directory not found: {input_dir}")

    os.makedirs(output_dir, exist_ok=True)

    parquet_files = []
    for entry in sorted(os.scandir(input_dir), key=lambda e: e.name):
        if entry.name.lower().endswith(".parquet") and entry.is_file():
            parquet_files.append(entry.name)

    if not parquet_files:
        sys.exit(f"No .parquet files found in {input_dir}")

    print(f"Found {len(parquet_files)} Parquet file(s) to convert.\n")

    summary = []
    for fname in parquet_files:
        in_path = os.path.join(input_dir, fname)
        out_name = os.path.splitext(fname)[0] + ".csv"
        out_path = os.path.join(output_dir, out_name)

        if not os.path.isfile(in_path):
            print(f"Skipping missing file: {fname}")
            continue

        in_size_mb = os.path.getsize(in_path) / (1024 * 1024)
        print(f"Converting {fname} ({in_size_mb:.1f} MB)...")

        row_count, elapsed = convert_file(in_path, out_path, batch_size)

        out_size_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(
            f"  -> {out_name}: {row_count:,} rows, "
            f"{out_size_mb:.1f} MB, {elapsed:.1f}s\n"
        )

        summary.append(
            {
                "file": fname,
                "rows": row_count,
                "parquet_mb": round(in_size_mb, 1),
                "csv_mb": round(out_size_mb, 1),
                "seconds": round(elapsed, 1),
            }
        )

    print("=" * 60)
    print("Conversion summary (save this for your report's Section 5):")
    print("=" * 60)
    total_rows = 0
    total_parquet_mb = 0.0
    total_csv_mb = 0.0
    for s in summary:
        print(
            f"{s['file']:35s} rows={s['rows']:>12,}  "
            f"parquet={s['parquet_mb']:>8.1f}MB  csv={s['csv_mb']:>8.1f}MB  "
            f"time={s['seconds']:>6.1f}s"
        )
        total_rows += s["rows"]
        total_parquet_mb += s["parquet_mb"]
        total_csv_mb += s["csv_mb"]

    print("-" * 60)
    print(f"TOTAL rows: {total_rows:,}")
    print(f"TOTAL parquet size: {total_parquet_mb:.1f} MB")
    if total_parquet_mb > 0:
        print(
            f"TOTAL csv size: {total_csv_mb:.1f} MB  "
            f"(growth factor: {total_csv_mb / total_parquet_mb:.2f}x)"
        )
    else:
        print(f"TOTAL csv size: {total_csv_mb:.1f} MB")


def main():
    # If no command-line arguments were passed (e.g. VS Code's Run button),
    # fall back to the DEFAULT_* values defined above instead of erroring out.
    if len(sys.argv) == 1:
        print("No command-line arguments detected — using DEFAULT_* values from the script.\n")
        convert_all(DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, DEFAULT_BATCH_SIZE)
        return

    parser = argparse.ArgumentParser(description="Convert TLC Parquet files to CSV.")
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing .parquet files",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write .csv files to",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=250_000,
        help="Rows per batch read into memory at once (default: 250000)",
    )
    args = parser.parse_args()

    convert_all(args.input_dir, args.output_dir, args.batch_size)


if __name__ == "__main__":
    main()
