import pandas as pd

def eda_summary(df):
    print("Basic Summary Statistics")
    print(df.describe())

    print("\nTriage Level Distribution")
    print(df["triage_level"].value_counts())

    print("\nAverage Waiting Time by Department")
    print(df.groupby("department")["waiting_time_minutes"].mean())

    print("\nAverage Waiting Time by Doctor")
    print(df.groupby("doctor_assigned")["waiting_time_minutes"].mean())

if __name__ == "__main__":
    df = pd.read_csv("../data/synthetic_ed_data_clean.csv")
    eda_summary(df)