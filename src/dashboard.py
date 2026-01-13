import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("../data/synthetic_ed_data_clean.csv")

st.title("Emergency Department Wait Time Dashboard")

st.header("Overall Waiting Time Distribution")
fig1 = px.histogram(df, x="waiting_time_minutes", nbins=40)
st.plotly_chart(fig1)

st.header("Average Waiting Time by Department")
fig2 = px.bar(
    df.groupby("department")["waiting_time_minutes"].mean().reset_index(),
    x="department",
    y="waiting_time_minutes"
)
st.plotly_chart(fig2)

st.header("Waiting Time by Triage Level")
fig3 = px.box(df, x="triage_level", y="waiting_time_minutes")
st.plotly_chart(fig3)

st.header("Doctor Performance Comparison")
fig4 = px.bar(
    df.groupby("doctor_assigned")["waiting_time_minutes"].mean().reset_index(),
    x="doctor_assigned",
    y="waiting_time_minutes"
)
st.plotly_chart(fig4)