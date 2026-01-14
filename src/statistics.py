import pandas as pd
from scipy.stats import f_oneway

def triage_anova(df):
    groups = [
        df[df["triage_level"] == level]["waiting_time_minutes"]
        for level in sorted(df["triage_level"].unique())
    ]

    f_stat, p_value = f_oneway(*groups)
    return f_stat, p_value


if __name__ == "__main__":
    df = pd.read_csv("data/processed/cleaned_data.csv")
    f, p = triage_anova(df)
    print(f"F-statistic: {f}, P-value: {p}")