# ed-wait-time-optimizer
End-to-end pipeline for optimizing emergency department wait times

## Emergency Department Optimization

This project provides a complete data pipeline, analytics suite, and optional machine learning model to understand, analyze, and optimize patient wait times in an Emergency Department (ED).
It includes synthetic data generation, cleaning, exploratory analysis, bottleneck detection, and an interactive Streamlit dashboard.

## Features

• Synthetic ED dataset generation
• Data cleaning and preprocessing
• Exploratory data analysis
• Bottleneck detection (department, doctors, triage levels)
• Streamlit dashboard with interactive visuals
• SQL schema and example queries
• Extendable ML model for wait time prediction
• Optional GitHub Actions CI/CD pipeline

## Repository Structure

Emergency-Department-Optimization
README.md
requirements.txt
data/
src/
data_generation.py
data_cleaning.py
eda.py
bottleneck_analysis.py
dashboard.py
utils.py
ml_wait_time_predictor.py
sql/
schema.sql
queries.sql
.github/workflows/
ci.yml

## Installation

1. Clone repo
git clone https://github.com/MEROO1010/Emergency-Department-Optimization.git
2.Navigate to folder
cd Emergency-Department-Optimization
3.Install dependencies
pip install -r requirements.txt

## Run Project

Generate synthetic data
python src/data_generation.py

Clean data
python src/data_cleaning.py

Run EDA
python src/eda.py

Run dashboard
streamlit run src/dashboard.py

Train ML model
python src/ml_wait_time_predictor.py

## License
MIT License

