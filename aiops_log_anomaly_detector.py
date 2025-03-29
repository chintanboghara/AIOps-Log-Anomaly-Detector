import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import argparse
import sys
from datetime import datetime

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log Analysis with Anomaly Detection")
    parser.add_argument("--file", type=str, default="system_logs.txt", 
                        help="Path to the system log file (default: system_logs.txt)")
    args = parser.parse_args()
    main(args.file)
