# ed-wait-time-optimizer
End-to-end pipeline for optimizing emergency department wait times

# 🏥 Hospital Patient Volume Forecasting

Forecasting daily patient visits for a private hospital using time series
analysis to support operational planning and data-driven decision making.

---

## 📌 Business Objective
Private hospitals face fluctuating patient demand, which directly impacts:
- Staffing levels
- Resource utilization
- Patient waiting times

This project forecasts daily patient volume to help hospital management make
proactive operational decisions.

---

## 📊 Data
- Simulated daily patient visits (2 years)
- Includes weekly and yearly seasonality patterns
- Designed to reflect real private hospital demand behavior

---

## 🧠 Methods & Models
- Exploratory Data Analysis (EDA)
- Feature Engineering (lags, rolling averages, calendar features)
- Time Series Forecasting:
  - ARIMA
  - Prophet

---

## 📈 Model Evaluation
Models were evaluated using:
- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)

| Model   | MAE | RMSE |
|--------|-----|------|
| ARIMA  | 12.4 | 15.8 |
| Prophet | **9.1** | **12.3** |

Prophet was selected as the preferred model due to its accuracy and
interpretability.

---

## 🖥 Interactive Dashboard
A Streamlit dashboard allows users to:
- Select forecast horizon
- Visualize expected patient volume trends

---

## 🗄 Database Design
A SQL schema is included to demonstrate how forecasted data can be stored
and integrated into hospital reporting systems.

---

## 🛠 Tools & Technologies
- Python (Pandas, NumPy, Matplotlib)
- Prophet, Statsmodels
- SQL
- Streamlit

---

## 🎯 Role Alignment
This project was designed for **Data Analyst roles in private hospitals**,
emphasizing:
- Business understanding
- Interpretability
- Actionable insights

---

## 🚀 How to Run
```bash
pip install -r requirements.txt
python src/data_generation.py
streamlit run streamlit_app/app.py
