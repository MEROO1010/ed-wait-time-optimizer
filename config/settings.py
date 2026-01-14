import os

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data")
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config")

# Create directories if they don't exist
for path in [DATA_PATH, SRC_PATH, CONFIG_PATH]:
    os.makedirs(path, exist_ok=True)

# Data parameters
DEFAULT_N_PATIENTS = 5000
START_DATE = "2024-01-01"

# Medical settings
DEPARTMENTS = [
    "Emergency Medicine",
    "Cardiology",
    "Orthopedics",
    "Pediatrics",
    "Trauma",
    "General Surgery"
]

TRIAGE_LEVELS = [
    "Resuscitation",    # Immediate
    "Emergency",        # < 10 minutes
    "Urgent",           # < 30 minutes
    "Less Urgent",      # < 60 minutes
    "Non-Urgent"        # < 120 minutes
]

# Performance thresholds (in minutes)
WAIT_TIME_THRESHOLDS = {
    "Resuscitation": 5,
    "Emergency": 10,
    "Urgent": 30,
    "Less Urgent": 60,
    "Non-Urgent": 120
}

# Dashboard settings
DASHBOARD_TITLE = "🏥 Emergency Department Analytics"
DASHBOARD_LAYOUT = "wide"
DASHBOARD_THEME = "light"

# Chart colors
CHART_COLORS = {
    "triage": ["#FF6B6B", "#FFD166", "#06D6A0", "#118AB2", "#073B4C"],
    "departments": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"],
    "outcomes": ["#2ECC71", "#3498DB", "#9B59B6", "#F39C12", "#E74C3C"]
}

# Email alerts (if implemented)
ALERT_RECIPIENTS = ["admin@hospital.com"]
ALERT_THRESHOLDS = {
    "avg_wait_time": 45,  # minutes
    "occupancy_rate": 0.85,  # 85%
    "admission_rate": 0.30  # 30%
}

# Database settings (for future implementation)
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ed_analytics",
    "user": "admin",
    "password": "secure_password"
}

# API settings (for future implementation)
API_CONFIG = {
    "base_url": "https://api.hospital.com/v1",
    "timeout": 30,
    "retries": 3
}

# Export settings
EXPORT_FORMATS = ["csv", "excel", "json", "html"]
DEFAULT_EXPORT_FORMAT = "csv"
EXPORT_ENCODING = "utf-8"