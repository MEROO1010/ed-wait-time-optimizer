import numpy as np
import pandas as pd

def generate_synthetic_ed_data(n=5000, seed=42):
    np.random.seed(seed)

    patient_ids = np.arange(1, n + 1)

    arrival_times = pd.date_range(
        start="2025-01-01 00:00",
        periods=n,
        freq="7min"
    )

    triage_levels = np.random.choice([1, 2, 3, 4, 5], size=n, p=[0.1, 0.2, 0.3, 0.25, 0.15])

    departments = np.random.choice(
        ["Cardiology", "Orthopedics", "General Medicine", "Neurology", "Pediatrics"],
        size=n
    )

    doctors = np.random.choice(
        ["Dr. Smith", "Dr. Lee", "Dr. Patel", "Dr. Chen", "Dr. Gomez"],
        size=n
    )

    waiting_times = np.clip(
        np.random.normal(loc=30 + triage_levels * 5, scale=10, size=n),
        0,
        240
    )

    treatment_time = np.clip(
        np.random.normal(loc=40 + triage_levels * 4, scale=15, size=n),
        5,
        300
    )

    discharge_status = np.random.choice(
        ["Discharged", "Admitted", "Transferred"],
        size=n,
        p=[0.75, 0.20, 0.05]
    )

    df = pd.DataFrame({
        "patient_id": patient_ids,
        "arrival_time": arrival_times,
        "triage_level": triage_levels,
        "department": departments,
        "doctor_assigned": doctors,
        "waiting_time_minutes": waiting_times,
        "treatment_time": treatment_time,
        "discharge_status": discharge_status
    })

    return df

if __name__ == "__main__":
    df = generate_synthetic_ed_data()
    df.to_csv("../data/synthetic_ed_data.csv", index=False)
    print("Synthetic dataset created.")