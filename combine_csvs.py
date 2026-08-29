#!/usr/bin/env python3
"""Combine multiple CSVs with identical headers into one CSV.

Usage:
  python combine_csvs.py out.csv input1.csv input2.csv ...

If an input path is not absolute, the script will also try to find it
under the workspace `CSV/` folder next to this repository.
"""
import os
import sys

THIS_DIR = os.path.dirname(__file__)
# CSV folder is sibling of the Project folder: ../CSV
CSV_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "CSV"))


def find_path(name):
    if os.path.isabs(name) and os.path.exists(name):
        return name
    if os.path.exists(name):
        return os.path.abspath(name)
    alt = os.path.join(CSV_DIR, name)
    if os.path.exists(alt):
        return alt
    return None


def combine(paths, out_path):
    first = True
    with open(out_path, "w", encoding="utf-8", newline="") as fout:
        for p in paths:
            real = find_path(p)
            if not real:
                print(f"Warning: input file not found: {p}", file=sys.stderr)
                continue
            with open(real, "r", encoding="utf-8") as fin:
                header = fin.readline()
                if first:
                    fout.write(header)
                    first = False
                # write remaining lines (skip header)
                for line in fin:
                    fout.write(line)
    print(f"Combined {len(paths)} files into: {out_path}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python combine_csvs.py out.csv input1.csv input2.csv ...")
        sys.exit(1)
    out = sys.argv[1]
    inputs = sys.argv[2:]
    out_abspath = os.path.abspath(out)
    os.makedirs(os.path.dirname(out_abspath), exist_ok=True)
    combine(inputs, out_abspath)


if __name__ == "__main__":
    main()
