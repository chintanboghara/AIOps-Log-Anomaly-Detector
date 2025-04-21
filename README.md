# AIOps Log Anomaly Detector

This Python script provides a command-line tool for analyzing log files, identifying potential anomalies using the Isolation Forest algorithm. It parses log entries, extracts relevant features, and flags entries that deviate significantly from the norm, aiding in the detection of system issues or security events.

## Overview

System logs are often voluminous and complex, making manual inspection for errors or unusual behaviour time-consuming and inefficient. This tool automates the process by:

1.  Reading log entries from a specified file.
2.  Parsing them into a structured format.
3.  Engineering features relevant for anomaly detection (timestamp patterns, log level severity, message length).
4.  Applying the Isolation Forest algorithm to identify outliers based on these features.
5.  Reporting the detected anomalies clearly.

## Key Features

-   **Structured Log Parsing:** Converts raw text log entries into an organized Pandas DataFrame.
-   **Intelligent Feature Engineering:**
    -   Extracts timestamps for temporal analysis.
    -   Maps standard log levels (e.g., INFO, WARN, ERROR) to numerical scores.
    -   Calculates log message length as a feature.
-   **Isolation Forest Anomaly Detection:** Employs `scikit-learn`'s Isolation Forest to effectively identify unusual log patterns based on the engineered features.
-   **Flexible Input:** Accepts a custom log file path via a command-line argument.
-   **Robust Error Handling:** Gracefully manages file-not-found errors and skips potentially malformed log entries during parsing.
-   **Clear Output:** Presents detected anomalies along with their original log content for easy review.

## How It Works

The script follows a simple pipeline:

1.  **Read:** Loads log lines from the input file (`system_logs.txt` by default).
2.  **Parse:** Attempts to extract `timestamp`, `level`, and `message` from each line based on an assumed format (see below). Invalid lines or lines with unparseable timestamps are skipped.
3.  **Feature Engineering:** Converts the parsed data into numerical features suitable for machine learning (numeric timestamp, level score, message length).
4.  **Detect:** Trains an Isolation Forest model on the features and predicts which log entries are anomalies (`-1` indicates an anomaly, `1` indicates normal).
5.  **Report:** Prints the original log entries identified as anomalies to the console.

## Expected Log Format

The script currently assumes a specific log format to parse entries correctly. It expects lines to generally follow this structure:

```
<Timestamp> [<LEVEL>] <Message>
```

**Examples of expected lines:**

```
2023-10-27 10:00:01 [INFO] System started successfully.
2023-10-27 10:05:30 [WARN] Low disk space detected on /var/log.
2023-10-27 10:15:00 [ERROR] Failed to connect to database: timeout expired.
```

**Important:**

-   The timestamp should be in a format recognizable by `pandas.to_datetime` (e.g., `YYYY-MM-DD HH:MM:SS`).
-   The log level should be enclosed in square brackets (e.g., `[INFO]`, `[DEBUG]`, `[ERROR]`). Common levels like `INFO`, `WARN`, `ERROR`, `DEBUG`, `CRITICAL`, `FATAL` are mapped to scores. Other levels might be treated as a default score or cause parsing issues if the structure deviates significantly.
-   The rest of the line after the level tag is considered the message.

If your log files use a different format, you will need to modify the `parse_logs` function in the `aiops_log_anomaly_detector.py` script accordingly.

##  Prerequisites

-   Python 3.6 or higher
-   Required Python packages:
    -   `pandas`
    -   `numpy`
    -   `scikit-learn`

## Installation

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone https://github.com/chintanboghara/AIOps-Log-Anomaly-Detector.git
    cd AIOps-Log-Anomaly-Detector
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    You can install the required packages using `pip`:
    ```bash
    pip install pandas numpy scikit-learn
    ```
    Or, if a `requirements.txt` file is provided in the repository:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script from your terminal within the project directory (and with the virtual environment activated, if used).

### Default Log File

The script defaults to using `system_logs.txt` in the current directory.

```bash
python aiops_log_anomaly_detector.py
```

### Custom Log File

Specify a different log file using the `--file` argument:

```bash
python aiops_log_anomaly_detector.py --file /path/to/your/log_file.log
```

### Example Output

If anomalies are detected, the script will print them like this:

```
Detected Anomalies:
-------------------
Log Entry: 2023-10-27 11:35:05 [ERROR] Unusual spike in CPU usage detected: 99%
Log Entry: 2023-10-27 12:01:00 [INFO] aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
Log Entry: 1970-01-01 00:00:00 [FATAL] System crash imminent! Core dump initiated.
-------------------
```

## Script Breakdown

-   **`read_logs(file_path: str) -> list`:**
    Reads lines from the specified `file_path`. Handles `FileNotFoundError` and returns a list of strings (log lines).
-   **`parse_logs(logs: list) -> pd.DataFrame`:**
    Takes a list of raw log strings. Attempts to parse each line into `timestamp`, `level`, and `message` components based on the expected format. Uses regular expressions for extraction. Converts timestamps using `pd.to_datetime` (coercing errors to `NaT`) and drops rows with invalid timestamps. Returns a structured Pandas DataFrame.
-   **`feature_engineering(df: pd.DataFrame) -> pd.DataFrame`:**
    Adds new features to the DataFrame:
    -   `timestamp_unix`: Converts the datetime timestamp to a Unix epoch integer for numerical analysis.
    -   `level_score`: Maps log levels (INFO, WARN, ERROR, etc.) to numerical scores. Unknown levels get a default score.
    -   `message_length`: Calculates the character length of the log message.
    Returns the enhanced DataFrame.
-   **`detect_anomalies(df: pd.DataFrame, contamination: float = 0.1) -> pd.DataFrame`:**
    Applies the Isolation Forest algorithm to the engineered features (`timestamp_unix`, `level_score`, `message_length`).
    -   The `contamination` parameter (default: 0.1 or 10%) estimates the proportion of outliers in the data. Adjust this value in the script if needed, based on domain knowledge.
    -   Adds an `anomaly` column to the DataFrame, where `-1` indicates a detected anomaly and `1` indicates a normal entry.
    Returns the DataFrame with the anomaly predictions.
-   **`main(file_path: str)`:**
    Orchestrates the entire process: calls `read_logs`, `parse_logs`, `feature_engineering`, and `detect_anomalies`. Filters the results to identify anomalies and prints them to the console. Includes checks for empty or unparseable logs.

## Configuration

-   **Contamination Factor:** The sensitivity of the anomaly detection is influenced by the `contamination` parameter within the `detect_anomalies` function (currently defaulted to `0.1`). This value represents the expected proportion of anomalies in your dataset. You can modify this value directly in the script (`aiops_log_anomaly_detector.py`) if you have a better estimate for your specific logs. A lower value makes the detection stricter (fewer anomalies flagged), while a higher value makes it more sensitive (more anomalies flagged).

## Troubleshooting

-   **`FileNotFoundError`:** Double-check that the path provided via `--file` is correct and the file exists. If using the default `system_logs.txt`, ensure it's in the same directory where you run the script.
-   **No Anomalies Detected:** This could be normal if your log file contains no significant outliers according to the algorithm and features used. You might experiment with the `contamination` parameter in the script.
-   **Very Few or No Parsed Logs:** If the script reports "No valid log entries found" or processes very few lines, your log file format likely differs significantly from the expected format (see "Expected Log Format" section). You'll need to adjust the parsing logic in the `parse_logs` function.
-   **Timestamp Parsing Errors:** Lines with timestamps that `pandas.to_datetime` cannot parse will be dropped. Check your log file for inconsistent or unsupported timestamp formats.
-   **Performance:** For extremely large log files (many millions of lines), the script might consume significant memory and time. Consider processing logs in chunks or using more advanced stream processing techniques for very large datasets.
