import pandas as pd

def clean_ed_data(df):
    df = df.copy()

    df["arrival_time"] = pd.to_datetime(df["arrival_time"])

    df["waiting_time_minutes"] = pd.to_numeric(df["waiting_time_minutes"], errors="coerce")
    df["treatment_time"] = pd.to_numeric(df["treatment_time"], errors="coerce")

    df = df.drop_duplicates(subset=["patient_id"])

    df = df[(df["waiting_time_minutes"] >= 0) & (df["waiting_time_minutes"] <= 600)]
    df = df[(df["treatment_time"] >= 0) & (df["treatment_time"] <= 600)]

    df = df.dropna()

    return df

if __name__ == "__main__":
    df = pd.read_csv("../data/synthetic_ed_data.csv")
    df_clean = clean_ed_data(df)
    df_clean.to_csv("../data/synthetic_ed_data_clean.csv", index=False)
    print("Data cleaned and saved.")