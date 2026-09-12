import streamlit as st
import plotly.express as px
from analytics import load_data, clean_data, compute_kpis

st.set_page_config(page_title="IT Operations Analytics", layout="wide")

st.title("🖥️ IT Operations Analytics Dashboard")

# Load and process data
raw_df = load_data()
df = clean_data(raw_df)
kpis = compute_kpis(df)

# Display KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Logs Processed", kpis["total_logs"])
col2.metric("Critical Events", kpis["critical_events"])
col3.metric("Avg Resolution Time (min)", f"{kpis['avg_resolution']}m")
col4.metric("SLA Breaches", kpis["sla_breaches"])

st.subheader("System Logs Overview")
st.dataframe(df.head(20))
