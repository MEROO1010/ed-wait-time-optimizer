import pandas as pd

def eda_summary(df):
    summary = {
        "total_patients": len(df),
        "avg_waiting_time": df["waiting_time_minutes"].mean(),
        "median_waiting_time": df["waiting_time_minutes"].median(),
        "avg_treatment_time": df["treatment_time"].mean(),
        "triage_distribution": df["triage_level"].value_counts().to_dict(),
        "department_load": df["department"].value_counts().to_dict()
    }

    return summary


if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_data.csv")
    print(eda_summary(df))