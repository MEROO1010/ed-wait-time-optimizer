import pandas as pd

def detect_bottlenecks(df):
    bottlenecks = {}

    dept_wait = df.groupby("department")["waiting_time_minutes"].mean().sort_values(ascending=False)
    bottlenecks["departments"] = dept_wait

    doctor_wait = df.groupby("doctor_assigned")["waiting_time_minutes"].mean().sort_values(ascending=False)
    bottlenecks["doctors"] = doctor_wait

    triage_wait = df.groupby("triage_level")["waiting_time_minutes"].mean().sort_values(ascending=False)
    bottlenecks["triage"] = triage_wait

    return bottlenecks

if __name__ == "__main__":
    df = pd.read_csv("../data/synthetic_ed_data_clean.csv")
    b = detect_bottlenecks(df)
    print("Bottlenecks detected:")
    print(b)