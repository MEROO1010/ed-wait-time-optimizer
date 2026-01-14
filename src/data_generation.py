import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)

NUM_PATIENTS = 5000

def generate_ed_data(num_patients=NUM_PATIENTS):
    patient_ids = [f"P{100000+i}" for i in range(num_patients)]

    start_date = datetime(2024, 1, 1)
    arrival_times = [
        start_date + timedelta(minutes=random.randint(0, 60 * 24 * 180))
        for _ in range(num_patients)
    ]

    triage_levels = np.random.choice(
        [1, 2, 3, 4, 5],
        size=num_patients,
        p=[0.05, 0.15, 0.4, 0.25, 0.15]
    )

    departments = ["ER", "Trauma", "Cardiology", "Neurology", "Pediatrics"]
    department_choices = np.random.choice(departments, num_patients)

    doctors = [f"Dr_{name}" for name in ["Ahmed", "Sara", "John", "Lina", "Omar"]]
    doctor_assigned = np.random.choice(doctors, num_patients)

    waiting_time = [
        max(5, int(np.random.normal(120 - t * 15, 20)))
        for t in triage_levels
    ]

    treatment_time = [
        max(15, int(np.random.normal(60 + t * 20, 30)))
        for t in triage_levels
    ]

    discharge_status = np.random.choice(
        ["Discharged", "Admitted", "Transferred"],
        size=num_patients,
        p=[0.65, 0.25, 0.10]
    )

    df = pd.DataFrame({
        "patient_id": patient_ids,
        "arrival_time": arrival_times,
        "triage_level": triage_levels,
        "department": department_choices,
        "doctor_assigned": doctor_assigned,
        "waiting_time_minutes": waiting_time,
        "treatment_time": treatment_time,
        "discharge_status": discharge_status
    })

    return df


# في آخر الملف
from pathlib import Path

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent
    raw_dir = BASE_DIR / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    df = generate_ed_data()
    df.to_csv(raw_dir / "ed_waiting_times.csv", index=False)