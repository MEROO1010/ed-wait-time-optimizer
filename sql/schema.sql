CREATE TABLE emergency_department (
    patient_id INT PRIMARY KEY,
    arrival_time TIMESTAMP,
    triage_level INT,
    department VARCHAR(50),
    doctor_assigned VARCHAR(50),
    waiting_time_minutes FLOAT,
    treatment_time FLOAT,
    discharge_status VARCHAR(20)
);