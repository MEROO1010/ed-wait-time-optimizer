CREATE TABLE emergency_visits (
    patient_id VARCHAR(20) PRIMARY KEY,
    arrival_time TIMESTAMP,
    triage_level INT,
    department VARCHAR(50),
    doctor_assigned VARCHAR(50),
    waiting_time_minutes INT,
    treatment_time INT,
    discharge_status VARCHAR(20)
);