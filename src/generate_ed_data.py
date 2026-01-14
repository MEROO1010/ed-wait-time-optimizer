import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_ed_data(rows=5000):
    # Create directory if it doesn't exist
    os.makedirs("data", exist_ok=True) 
    np.random.seed(42)

    departments = ["Emergency", "Cardiology", "Orthopedics", "Pediatrics", "General Surgery"]
    triage_categories = ["Resuscitation", "Emergency", "Urgent", "Less Urgent", "Non-Urgent"]

    base_time = datetime(2024, 1, 1, 8, 0, 0)
    arrival_times = []

    # Logic to generate arrival times
    for i in range(rows):
        hour = (base_time.hour + i // 60) % 24
        if 8 <= hour <= 20:
            minutes_to_add = np.random.exponential(5)
        else:
            minutes_to_add = np.random.exponential(15)
        arrival_times.append(base_time + timedelta(minutes=minutes_to_add * i))

    df = pd.DataFrame({
        "patient_id": np.arange(10001, 10001 + rows),
        "arrival_time": arrival_times,
        "triage_category": np.random.choice(triage_categories, rows, p=[0.05, 0.15, 0.30, 0.30, 0.20]),
        "department": np.random.choice(departments, rows, p=[0.40, 0.15, 0.15, 0.15, 0.15]),
        "doctor_id": np.random.choice([f"DR{i:03d}" for i in range(1, 26)], rows),
        "wait_time_min": np.random.exponential(45, rows).round(1),
        "treatment_time_min": np.random.normal(60, 20, rows).clip(10, 180).round(1),
        "age": np.random.randint(1, 100, rows),
        "gender": np.random.choice(["M", "F"], rows, p=[0.48, 0.52]),
        "outcome": np.random.choice(
            ["Discharged", "Admitted", "Transferred", "Observation"],
            rows,
            p=[0.60, 0.25, 0.10, 0.05]
        )
    })

    # Adjust wait time based on triage priority
    df["wait_time_min"] *= df["triage_category"].map({
        "Resuscitation": 0.1,
        "Emergency": 0.5,
        "Urgent": 1.0,
        "Less Urgent": 1.5,
        "Non-Urgent": 2.0
    })

    csv_path = "data/emergency_department_data.csv"
    df.to_csv(csv_path, index=False)

    print(f"CSV created: {csv_path}")
    return df

# Corrected main block
if __name__ == "__main__": 
    generate_ed_data(5000)
