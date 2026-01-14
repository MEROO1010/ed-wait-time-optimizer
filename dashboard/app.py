from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned_data.csv"

df = pd.read_csv(DATA_PATH)
df["arrival_time"] = pd.to_datetime(df["arrival_time"])

st.title("🏥 Emergency Department Waiting Time Optimization")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.box(
        df,
        x="triage_level",
        y="waiting_time_minutes",
        title="Waiting Time by Triage Level"
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(
        df.groupby("department")["waiting_time_minutes"].mean().reset_index(),
        x="department",
        y="waiting_time_minutes",
        title="Average Waiting Time by Department"
    )
    st.plotly_chart(fig2, use_container_width=True)

fig3 = px.histogram(
    df,
    x="waiting_time_minutes",
    nbins=50,
    title="Distribution of Waiting Times"
)
st.plotly_chart(fig3, use_container_width=True)