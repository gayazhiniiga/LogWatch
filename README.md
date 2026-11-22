# LogWatch
https://logwatch-security.streamlit.app/
LogWatch is a Python and Streamlit dashboard for reviewing authentication log
CSV files. It summarizes login outcomes and highlights IP addresses whose
failed-login counts meet a user-configured threshold.

LogWatch analyses files supplied by the user or its bundled sample. It does
not monitor systems in real time. A flagged IP represents potentially
suspicious activity, not a confirmed attack or attribution.

## Project overview

The dashboard combines one or more uploaded CSV files, validates each file's
required columns, and passes the combined records to the existing analysis
function in `main.py`. When no files are uploaded, it uses `login_logs.csv`.

## Features

- Accepts a single CSV or multiple CSV files in one upload.
- Validates the required columns in each file and identifies rejected files.
  Valid files are still analysed when other selected files are invalid.
- Combines valid files before analysis, so failed attempts from the same IP
  are counted across files. Duplicate rows are retained and counted.
- Provides a synchronized slider and numeric input for a threshold from 1 to
  10; the default is 3.
- Shows total attempts, successful and failed logins, suspicious IPs, flagged
  IPs, failed attempts from flagged IPs, and the active threshold.
- Displays suspicious IP cards with attempt counts, a share-of-flagged-attempts
  progress bar, and threshold status.
- Supports searching flagged IPs, sorting by highest or lowest failed-attempt
  count, and pagination with 5 or 10 cards per page.
- Charts failed-login attempts by IP and displays authentication records in a
  table.
- Supports Streamlit's light and dark themes, with theme-aware dashboard
  styling.
- Uses the built-in `login_logs.csv` when no upload is selected.

## Technologies used

- Python
- Streamlit
- pandas
- Plotly
- Python standard library (`csv`, `io`, `pathlib`, and other utilities)

The dashboard dependencies are listed without pinned versions in
`requirements.txt`.

## Project folder structure

```text
.
├── .streamlit/
│   └── config.toml
├── app.py
├── login_logs.csv
├── logwatch_synthetic_upload_test_1.csv
├── logwatch_threshold_test_2.csv
├── main.py
├── README.md
├── requirements.txt
└── synthetic_login_activity_dataset.csv
```

The additional CSV files shown above are present in the project folder and can
be selected for analysis. Only `login_logs.csv` is loaded automatically when
there is no upload. The local virtual environment and Python cache are omitted
from this source-oriented tree.

## CSV input format

Each uploaded file must have a header containing these columns:

```csv
timestamp,ip_address,status
2026-11-22T09:10:00Z,198.51.100.10,FAILED
2026-11-22T09:12:00Z,198.51.100.10,SUCCESS
```

- Column names are trimmed and treated case-insensitively.
- `status` must be `FAILED` or `SUCCESS` (case-insensitive).
- Rows with an empty timestamp or IP address, or an unsupported status, are
  skipped and counted as invalid or incomplete.
- Extra columns are not used in analysis.
- Files are read as UTF-8; a UTF-8 byte-order mark is supported.
- The uploader displays a 200 MB per-file limit, subject to the Streamlit
  server configuration.

If a file cannot be read or is missing a required column, LogWatch reports the
file name and reason. Other valid files continue through analysis. If none of
the selected files are valid, LogWatch displays an error instead of running the
analysis.

## Installation on Windows

Install Python and open PowerShell in the project directory:

```powershell
cd "C:\path\to\failed login attempt analyser"
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the Python launcher `py` is unavailable, use `python -m venv .venv`.

## Run the application

From the project directory, run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit prints a local URL (typically `http://localhost:8501`) to open in
your browser. Use the sidebar to adjust the threshold or select one or more
CSV files.

## How detection works

The analysis function in `main.py` trims input values, normalizes status text,
and counts `FAILED` records by IP address. An IP is flagged when its combined
failed-attempt count is greater than or equal to the selected threshold.
`SUCCESS` records contribute to the login metrics but not to the failed-login
count. Incomplete rows and rows with unsupported statuses are skipped.

For example, with a threshold of 3:

| File | IP address | Failed attempts |
| --- | --- | ---: |
| `part-a.csv` | `198.51.100.10` | 2 |
| `part-b.csv` | `198.51.100.10` | 1 |

LogWatch combines the files before analysis, so this IP has 3 failed attempts
and appears as flagged. If the threshold is 4, it does not meet the threshold.
Repeated rows are counted as separate log entries; LogWatch does not deduplicate
them.

## Testing performed

The application was checked with Streamlit AppTest and a live Streamlit
startup. Checks covered:

- Single-file and multiple-file uploads.
- Aggregation of failed attempts for the same IP across files.
- Preservation of duplicate rows and timestamp ordering.
- File-level validation, mixed valid/invalid uploads, and the all-invalid case.
- Slider/numeric-input synchronization and threshold-driven metric updates.
- The 1-10 threshold range and default value of 3.

The current development environment used Python 3.14.10 and Streamlit 1.67.0.
No standalone test suite is included in the project folder.

## Limitations

- LogWatch analyses uploaded or bundled CSV data; it is not a live monitoring
  agent, SIEM, or alerting service.
- A threshold match is a heuristic signal only. LogWatch does not confirm
  attacks, identify an actor, or establish that an IP is malicious.
- Failed attempts are aggregated over all records supplied for that analysis;
  there is no configurable time window.
- Timestamps are required and used for ordering when parseable, but their date
  format is not strictly validated by the detection function.
- Analysis is based on the provided fields and does not enrich IPs with
  reputation, geolocation, ownership, or other context.
- Uploads are processed in memory. Large collections of files may require
  additional memory.

## Future improvements

- Add strict timestamp validation and configurable time-window analysis.
- Add a persistent automated test suite for parsing, validation, and detection.
- Support configurable status mappings and additional authentication schemas.
- Add optional, clearly sourced IP context or reputation enrichment.
- Add a workflow for saving and reviewing analysis results over time.
