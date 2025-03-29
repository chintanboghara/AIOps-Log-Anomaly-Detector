# Explanation of the AIOps Log Analysis and Anomaly Detection Script

This document provides a comprehensive explanation of the Python script used for log analysis and anomaly detection. The script is organized into well-defined functions for clarity, ease of testing, and improved error handling.

## Overview

The script performs the following key tasks:
- **Reading Logs:** Reads a system log file containing raw log entries.
- **Parsing Logs:** Converts raw log lines into a structured format using a Pandas DataFrame.
- **Feature Engineering:** Enhances the DataFrame with numerical features derived from the log level and message length.
- **Anomaly Detection:** Uses the Isolation Forest algorithm from scikit-learn to identify anomalous log entries.
- **Command-Line Interface:** Allows users to specify a log file path via command-line arguments.

## Detailed Breakdown

### 1. Import Statements

```python
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import argparse
import sys
from datetime import datetime
```

- **Pandas & NumPy:** For data manipulation and numerical operations.
- **IsolationForest:** An unsupervised machine learning model for anomaly detection.
- **Argparse & Sys:** To handle command-line arguments and system exit conditions.
- **Datetime:** For working with and parsing timestamps.

### 2. Reading Log Files: `read_logs`

```python
def read_logs(file_path: str) -> list:
    """
    Reads a log file and returns a list of log lines.
    """
    try:
        with open(file_path, "r") as file:
            logs = file.readlines()
        return logs
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)
```

- **Purpose:** Opens the log file and reads its content into a list.
- **Error Handling:** Catches file not found errors and other exceptions, printing an error message and exiting gracefully.

### 3. Parsing Logs: `parse_logs`

```python
def parse_logs(logs: list) -> pd.DataFrame:
    """
    Parses log lines into a structured DataFrame with columns:
    ['timestamp', 'level', 'message'].
    """
    data = []
    for log in logs:
        # Split line into parts; ensuring the message field may include spaces.
        parts = log.strip().split(" ", 3)
        if len(parts) < 4:
            continue  # Skip malformed lines
        timestamp_str = parts[0] + " " + parts[1]
        level = parts[2]
        message = parts[3]
        data.append([timestamp_str, level, message])
    
    df = pd.DataFrame(data, columns=["timestamp", "level", "message"])
    # Convert timestamp to datetime with error coercion
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"])  # Remove rows with invalid timestamps
    return df
```

- **Splitting Log Lines:** Each log entry is split into its components. The `split(" ", 3)` ensures that the message (which may contain spaces) remains intact.
- **DataFrame Creation:** The parsed data is loaded into a Pandas DataFrame with columns for timestamp, log level, and message.
- **Timestamp Conversion:** Converts the timestamp string to a datetime object. Any lines with improperly formatted timestamps are dropped.

### 4. Feature Engineering: `feature_engineering`

```python
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds numeric scores for log levels and computes message length.
    """
    # Map log levels to numeric scores
    level_mapping = {"INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
    df["level_score"] = df["level"].map(level_mapping).fillna(0)
    
    # Add a new feature: message length
    df["message_length"] = df["message"].apply(len)
    return df
```

- **Mapping Log Levels:** Assigns a numeric value to each log level, facilitating numerical analysis.
- **Message Length Feature:** Calculates the length of each log message, providing an additional feature for anomaly detection.

### 5. Anomaly Detection: `detect_anomalies`

```python
def detect_anomalies(df: pd.DataFrame, contamination: float = 0.1) -> pd.DataFrame:
    """
    Uses IsolationForest to detect anomalies based on level score and message length.
    """
    # Initialize Isolation Forest
    model = IsolationForest(contamination=contamination, random_state=42)
    # Fit the model and predict anomalies
    df["anomaly"] = model.fit_predict(df[["level_score", "message_length"]])
    # Convert prediction to a readable format
    df["is_anomaly"] = df["anomaly"].apply(lambda x: "❌ Anomaly" if x == -1 else "✅ Normal")
    return df
```

- **Model Initialization:** An Isolation Forest is created with a specified contamination rate and a fixed random state for reproducibility.
- **Fitting and Predicting:** The model is trained on the `level_score` and `message_length` features. It outputs `-1` for anomalies and `1` for normal entries.
- **Readable Output:** The predictions are translated into human-readable labels ("❌ Anomaly" or "✅ Normal").

### 6. Main Function and Command-Line Interface: `main`

```python
def main(file_path: str):
    logs = read_logs(file_path)
    df = parse_logs(logs)
    if df.empty:
        print("No valid log entries found.")
        sys.exit(0)
    df = feature_engineering(df)
    df = detect_anomalies(df, contamination=0.1)
    
    # Filter and print only detected anomalies
    anomalies = df[df["is_anomaly"] == "❌ Anomaly"]
    if anomalies.empty:
        print("\n🔍 No anomalies detected.")
    else:
        print("\n🔍 **Detected Anomalies:**\n", anomalies)
```

- **Integrating Steps:** The `main` function orchestrates the entire process:
  - Reading and parsing logs.
  - Applying feature engineering.
  - Detecting anomalies.
- **Output:** Only anomalies are filtered and printed. If no anomalies are found, an appropriate message is displayed.

### 7. Script Execution Guard

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Analysis with Anomaly Detection")
    parser.add_argument("--file", type=str, default="system_logs.txt", 
                        help="Path to the system log file (default: system_logs.txt)")
    args = parser.parse_args()
    main(args.file)
```

- **Command-Line Parsing:** Uses `argparse` to allow users to provide a custom log file path.
- **Execution Guard:** Ensures that the script only runs when executed directly, not when imported as a module.
