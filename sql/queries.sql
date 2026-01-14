-- Average waiting time per department
SELECT department, AVG(waiting_time_minutes) AS avg_wait
FROM emergency_visits
GROUP BY department;

-- Doctor workload analysis
SELECT doctor_assigned, COUNT(*) AS patient_count
FROM emergency_visits
GROUP BY doctor_assigned;

-- Critical triage waiting times
SELECT *
FROM emergency_visits
WHERE triage_level <= 2 AND waiting_time_minutes > 30;