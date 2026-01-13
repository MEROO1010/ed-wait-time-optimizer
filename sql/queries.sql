SELECT department, AVG(waiting_time_minutes)
FROM emergency_department
GROUP BY department
ORDER BY AVG(waiting_time_minutes) DESC;

SELECT triage_level, COUNT(*)
FROM emergency_department
GROUP BY triage_level;

SELECT doctor_assigned, AVG(waiting_time_minutes)
FROM emergency_department
GROUP BY doctor_assigned;