# src/data_cleaning.py

import pandas as pd
from pathlib import Path

def clean_data(filepath):
    df = pd.read_csv(filepath)
    df["arrival_time"] = pd.to_datetime(df["arrival_time"])
    df = df[df["waiting_time_minutes"] >= 0]
    df = df[df["treatment_time"] > 0]
    df.dropna(inplace=True)
    return df


if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    raw_path = BASE_DIR / "data" / "raw" / "ed_waiting_times.csv"
    processed_dir = BASE_DIR / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    cleaned_df = clean_data(raw_path)
    cleaned_df.to_csv(processed_dir / "cleaned_data.csv", index=False)