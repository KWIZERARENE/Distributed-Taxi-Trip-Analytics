# Code Appendix — Distributed Taxi Trip Analytics

This folder collects, in one place, the source code referenced throughout
`Taxi_Analytics_Report.docx`, so the pipeline can be read end-to-end and
explained without hunting through separate project folders.

## What's genuinely yours vs. reconstructed here

- **`parquet_to_csv.py`** — this is your actual script, copied verbatim from
  what you provided. No changes were made to its logic.
- **Every other file** (`mapper_*.py` / `reducer_*.py` / `pandas_hourly.py`)
  was **reconstructed from the exact specification already written in your
  report** (Section 6.1's validation rules, Table 7.1's key/value design,
  Section 9.8's duration buckets, and the anomaly counter names in Section
  9.9 — which match your real `hdfs dfs -cat .../anomalies/part-00000`
  output byte-for-byte: `MISSING_BASE_NUMBER`, `SAME_PICKUP_DROPOFF_ZONE`,
  `TOTAL_RECORDS_SCANNED`, `VERY_LONG_TRIP_OVER_3H`,
  `VERY_SHORT_TRIP_UNDER_1MIN`). They were smoke-tested on a small sample
  and produce the expected keys and behavior.

**Before you submit or present this as "the" project code, swap these
reconstructions out for your real, already-tested files** — they were built
to match your documented design so you have something correct to compare
against and to study, not to replace your actual submitted work.

## Combining the 4 months (Jan–Apr 2026)

All four raw CSVs are already on HDFS at `/taxi_project/input/raw/CSV/`
(confirmed by your own `hdfs dfs -ls -R` output). Combining them requires
**exactly one change, and it's a command-line argument, not a code file**:

- **Old cleaning-job input:** `/taxi_project/input/raw/CSV/fhv_tripdata_2026-01.csv`
- **New cleaning-job input:** `/taxi_project/input/raw/CSV` (the folder)

Hadoop Streaming treats every file inside an input folder as part of the
job automatically, so pointing at the folder instead of one filename
combines all four months for free. **No mapper or reducer `.py` file needs
to change** — `mapper_cleaning.py`'s header-skip check matches the header
*by its exact text*, not "first line of input", so it correctly skips one
header per file regardless of how many files are combined, and every
downstream job already reads from `/taxi_project/input/cleaned` unchanged.

Run `run_pipeline_4months.bat` (included here) to do the whole rerun —
clear old outputs, reprocess the combined input, and pull every result
back to local disk — in one command. Its only editable settings are two
paths at the top (Hadoop Streaming jar location, script folder).

`pandas_hourly.py` was updated the same way on the single-machine side: it
now accepts a folder and concatenates every CSV in it, so the Pandas
comparison in Section 12 can be re-run fairly against the same combined
4-month dataset.

## Pipeline map

| Stage | Files | Reads | Writes |
|---|---|---|---|
| Format conversion | `parquet_to_csv.py` | local `.parquet` | local `.csv` |
| Cleaning | `mapper_cleaning.py`, `reducer_cleaning.py` | `/taxi_project/input/raw` | `/taxi_project/input/cleaned` |
| Hourly demand | `mapper_hourly.py`, `reducer_hourly.py` | cleaned data | `output/hourly` |
| Daily demand | `mapper_daily.py`, `reducer_daily.py` | cleaned data | `output/daily` |
| Zone ranking (Job 1) | `mapper_location.py`, `reducer_location.py` | cleaned data | `output/locations` |
| Zone ranking (Job 2) | `mapper_topn.py`, `reducer_topn.py` | `output/locations` | `output/locations_topn` |
| Route ranking (Job 1) | `mapper_route.py`, `reducer_route.py` | cleaned data | `output/routes` |
| Route ranking (Job 2) | `mapper_topn.py` (reused), `reducer_route_topn.py` | `output/routes` | `output/routes_top20` |
| Trip duration | `mapper_duration.py`, `reducer_duration.py` | cleaned data | `output/duration` |
| Anomaly detection | `mapper_anomaly.py`, `reducer_anomaly.py` | cleaned data | `output/anomalies` |
| Pandas comparison | `pandas_hourly.py` | raw CSV | console |

## How to explain each piece in one sentence

- **Conversion**: streams Parquet in batches so a multi-million-row month
  never has to fit in memory at once.
- **Cleaning**: a mapper validates/filters every raw line; the reducer
  dedupes by relying on Hadoop's sorted-key guarantee — no hash set needed.
- **Hourly/Daily/Location/Route**: identical "emit key→1, reducer sums
  consecutive matching keys" pattern — the same idea, four different keys.
- **Top-N (multi-stage)**: Job 1 aggregates to a small number of distinct
  keys; Job 2's mapper funnels everything to one constant key ("ALL") so a
  single reducer can sort globally — this is *why* it needs to be two jobs.
- **Duration/Anomaly**: same accumulate-and-flush reducer pattern, applied
  to a computed bucket / flag instead of a raw field.
