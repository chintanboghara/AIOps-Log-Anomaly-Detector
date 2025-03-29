# AIOps Log Analysis and Anomaly Detection Script

The script reads a log file (default: `system_logs.txt`), parses each entry into a structured Pandas DataFrame, and computes features like timestamp, log level, and message length. It then leverages an Isolation Forest algorithm to detect anomalous log entries based on these features. The anomalies are outputted in a clear, human-readable format.

## Features

- **Log Parsing:** Converts raw log entries into a structured DataFrame.
- **Feature Engineering:** Maps log levels to numeric scores and computes message lengths.
- **Anomaly Detection:** Uses the Isolation Forest algorithm to flag unusual log patterns.
- **Command-Line Interface:** Run the script with a custom log file path.
- **Error Handling:** Gracefully handles missing files or invalid log entries.

## Prerequisites

Before running the script, ensure that Python 3.6 or higher is installed. You will also need to install the required Python packages:

- [pandas](https://pandas.pydata.org/)
- [numpy](https://numpy.org/)
- [scikit-learn](https://scikit-learn.org/)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/chintanboghara/AIOps-Log-Anomaly-Detector.git
   cd AIOps-Log-Anomaly-Detector
   ```

2. **Install Dependencies:**

   You can install the required packages using `pip`:

   ```bash
   pip install pandas numpy scikit-learn
   ```

   Alternatively, if a `requirements.txt` file is available, run:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

The script can be run directly from the command line. By default, it will look for a log file named `system_logs.txt` in the same directory. To use a different file, supply the `--file` argument.

### Running the Script with Default Settings

```bash
python aiops_log_anomaly_detector.py
```

### Running the Script with a Custom Log File

```bash
python aiops_log_anomaly_detector.py --file path/to/log_file.txt
```

The script will output any detected anomalies in the terminal.

## Script Breakdown

- **read_logs(file_path: str):**  
  Reads the log file and returns a list of log entries. Includes error handling for missing files.

- **parse_logs(logs: list):**  
  Parses the raw log lines into a structured Pandas DataFrame with columns: `timestamp`, `level`, and `message`. Invalid timestamps are dropped.

- **feature_engineering(df: pd.DataFrame):**  
  Enhances the DataFrame by mapping log levels to numeric scores and computing the length of each message.

- **detect_anomalies(df: pd.DataFrame, contamination: float = 0.1):**  
  Uses an Isolation Forest to predict anomalies. Anomalous entries are labeled for easy identification.

- **main(file_path: str):**  
  The main driver function that integrates the steps above and outputs the final anomalies.

## Troubleshooting

- **File Not Found Error:**  
  Ensure that the file path provided with `--file` exists. The script will exit if it cannot locate the file.

- **Invalid Log Entries:**  
  The parser is designed to skip malformed lines. If no valid log entries are found, a message will be displayed.

- **Timestamp Parsing Issues:**  
  The script uses `pd.to_datetime` with error coercion. If timestamps are not in a valid format, they will be dropped from analysis.
