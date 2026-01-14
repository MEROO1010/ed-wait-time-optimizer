import pandas as pd

def detect_bottlenecks(df):
    dept_wait = (
        df.groupby("department")["waiting_time_minutes"]
        .mean()
        .sort_values(ascending=False)
    )

    doctor_wait = (
        df.groupby("doctor_assigned")["waiting_time_minutes"]
        .mean()
        .sort_values(ascending=False)
    )

    triage_wait = (
        df.groupby("triage_level")["waiting_time_minutes"]
        .mean()
    )

    return {
        "department_bottleneck": dept_wait,
        "doctor_bottleneck": doctor_wait,
        "triage_bottleneck": triage_wait
    }


if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_data.csv")
    results = detect_bottlenecks(df)
    print(results)