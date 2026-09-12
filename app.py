"""
app.py — IT Operations Analytics Dashboard (Streamlit)
Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from analytics import (
    load_data,
    clean_data,
    compute_kpis,
    compute_efficiency_scores,
    ticket_category_analysis,
    daily_metrics,
    summary_statistics,
)

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IT Operations Dashboard",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%);
        border-radius: 12px;
        padding: 16px 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
    }
    .metric-card h2 { margin: 0; font-size: 2rem; }
    .metric-card p  { margin: 0; font-size: 0.85rem; opacity: 0.85; }
    .status-critical { color: #ef4444; font-weight: bold; }
    .status-warning  { color: #f59e0b; font-weight: bold; }
    .status-resolved { color: #22c55e; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/server.png",
        width=80,
    )
    st.title("IT Ops Dashboard")
    st.caption("Institutional Data Analytics Pipeline")
    st.divider()

    st.subheader("🔍 Filters")
    status_filter = st.multiselect(
        "Server Status",
        options=["Resolved", "Warning", "Critical"],
        default=["Resolved", "Warning", "Critical"],
    )
    region_filter = st.multiselect(
        "Region",
        options=["North", "South", "East", "West"],
        default=["North", "South", "East", "West"],
    )
    st.divider()
    st.caption("📊 Data: IT Operations Log v1.0")
    st.caption("👤 Specialist: IT & Web Support")


# ── Load & Process Data ────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading and processing data…")
def get_data():
    raw = load_data()
    return clean_data(raw)


df_full = get_data()

# Apply sidebar filters
df = df_full[
    df_full["status"].isin(status_filter) & df_full["region"].isin(region_filter)
].copy()

if df.empty:
    st.warning("No data matches the selected filters. Please adjust filters.")
    st.stop()

kpis = compute_kpis(df)
eff_scores = compute_efficiency_scores(df)
ticket_analysis = ticket_category_analysis(df)
daily = daily_metrics(df)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🖥️ IT Operations Analytics Dashboard")
st.caption(
    f"Showing **{len(df)}** of **{len(df_full)}** records  |  "
    f"Regions: {', '.join(region_filter)}  |  Statuses: {', '.join(status_filter)}"
)
st.divider()

# ── KPI Row ────────────────────────────────────────────────────────────────────
st.subheader("📌 Key Performance Indicators")
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("✅ Avg Uptime", f"{kpis['avg_uptime_pct']}%", help="Average server uptime %")
k2.metric("⏱️ Avg Resolution", f"{kpis['avg_resolution_mins']} min",
          help="Average ticket resolution time in minutes")
k3.metric("🌐 Avg Bandwidth", f"{kpis['avg_bandwidth_mbps']} Mbps",
          help="Average network bandwidth")
k4.metric("🔴 Critical Events", kpis["critical_count"], help="Servers in critical status")
k5.metric("⚠️ Warnings", kpis["warning_count"], help="Servers with warnings")
k6.metric("⏬ Total Downtime", f"{kpis['total_downtime_hrs']} hrs",
          help="Cumulative downtime hours")

st.divider()

# ── Efficiency Scores + Status Pie ─────────────────────────────────────────────
col_eff, col_pie = st.columns([2, 1])

with col_eff:
    st.subheader("🏆 System Efficiency Scores by Server")
    color_map = {s: c for s, c in zip(
        eff_scores["server_name"],
        px.colors.qualitative.Bold[:len(eff_scores)],
    )}
    fig_eff = px.bar(
        eff_scores,
        x="server_name",
        y="efficiency_score",
        color="server_name",
        color_discrete_map=color_map,
        text="efficiency_score",
        labels={"efficiency_score": "Efficiency Score (0-100)", "server_name": "Server"},
        template="plotly_dark",
    )
    fig_eff.update_traces(textposition="outside", cliponaxis=False)
    fig_eff.update_layout(showlegend=False, yaxis_range=[0, 105], height=380)
    st.plotly_chart(fig_eff, use_container_width=True)

with col_pie:
    st.subheader("📊 Status Distribution")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    status_colors = {"Resolved": "#22c55e", "Warning": "#f59e0b", "Critical": "#ef4444"}
    fig_pie = px.pie(
        status_counts,
        names="status",
        values="count",
        color="status",
        color_discrete_map=status_colors,
        hole=0.45,
        template="plotly_dark",
    )
    fig_pie.update_layout(height=380, legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ── Daily Time-Series ──────────────────────────────────────────────────────────
st.subheader("📈 Daily Resource Utilisation Trends")

fig_trend = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "CPU Usage (%)", "Memory Usage (%)",
        "Network Bandwidth (Mbps)", "Total Downtime (mins)"
    ),
    shared_xaxes=True,
    vertical_spacing=0.12,
)

fig_trend.add_trace(
    go.Scatter(x=daily["date"], y=daily["avg_cpu"], mode="lines+markers",
               name="CPU", line=dict(color="#3b82f6", width=2)),
    row=1, col=1
)
fig_trend.add_trace(
    go.Scatter(x=daily["date"], y=daily["avg_memory"], mode="lines+markers",
               name="Memory", line=dict(color="#8b5cf6", width=2)),
    row=1, col=2
)
fig_trend.add_trace(
    go.Scatter(x=daily["date"], y=daily["avg_bandwidth"], mode="lines+markers",
               name="Bandwidth", line=dict(color="#06b6d4", width=2)),
    row=2, col=1
)
fig_trend.add_trace(
    go.Bar(x=daily["date"], y=daily["total_downtime_mins"],
           name="Downtime", marker_color="#ef4444"),
    row=2, col=2
)

fig_trend.update_layout(
    template="plotly_dark", height=480,
    showlegend=False,
    margin=dict(t=50, b=20),
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# ── Ticket Analysis ────────────────────────────────────────────────────────────
col_tkt, col_res = st.columns(2)

with col_tkt:
    st.subheader("🎫 Ticket Category Breakdown")
    fig_tkt = px.bar(
        ticket_analysis,
        x="ticket_category",
        y="ticket_count",
        color="ticket_category",
        text="ticket_count",
        template="plotly_dark",
        labels={"ticket_count": "Count", "ticket_category": "Category"},
    )
    fig_tkt.update_traces(textposition="outside")
    fig_tkt.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_tkt, use_container_width=True)

with col_res:
    st.subheader("⏱️ Avg Resolution Time by Category (mins)")
    fig_res = px.bar(
        ticket_analysis,
        x="avg_resolution_mins",
        y="ticket_category",
        orientation="h",
        color="avg_resolution_mins",
        color_continuous_scale="Blues",
        text="avg_resolution_mins",
        template="plotly_dark",
        labels={"avg_resolution_mins": "Avg Mins", "ticket_category": ""},
    )
    fig_res.update_traces(textposition="outside")
    fig_res.update_layout(coloraxis_showscale=False, height=350)
    st.plotly_chart(fig_res, use_container_width=True)

st.divider()

# ── Resource Heatmap ───────────────────────────────────────────────────────────
st.subheader("🗺️ Resource Usage Heatmap by Server & Region")
heat_df = df.groupby(["server_name", "region"])[
    ["cpu_usage_pct", "memory_usage_pct", "disk_usage_pct"]
].mean().round(1).reset_index()

heat_pivot = heat_df.pivot_table(
    index="server_name", columns="region", values="cpu_usage_pct", aggfunc="mean"
).fillna(0)

fig_heat = px.imshow(
    heat_pivot,
    color_continuous_scale="RdYlGn_r",
    aspect="auto",
    template="plotly_dark",
    title="Average CPU Usage % (Server × Region)",
    labels=dict(color="CPU %"),
)
fig_heat.update_layout(height=320)
st.plotly_chart(fig_heat, use_container_width=True)

st.divider()

# ── Scatter: CPU vs Memory ─────────────────────────────────────────────────────
st.subheader("🔬 CPU vs Memory Usage Scatter")
fig_scatter = px.scatter(
    df,
    x="cpu_usage_pct",
    y="memory_usage_pct",
    color="server_name",
    size="network_bandwidth_mbps",
    hover_data=["timestamp", "status", "ticket_category"],
    template="plotly_dark",
    labels={"cpu_usage_pct": "CPU Usage (%)", "memory_usage_pct": "Memory Usage (%)"},
)
fig_scatter.update_layout(height=400)
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

# ── Summary Statistics ─────────────────────────────────────────────────────────
with st.expander("📋 Summary Statistics", expanded=False):
    st.dataframe(summary_statistics(df), use_container_width=True)

# ── Filterable Log Viewer ──────────────────────────────────────────────────────
st.subheader("📄 Filterable Log Viewer")

server_opts = ["All"] + sorted(df["server_name"].unique().tolist())
selected_server = st.selectbox("Filter by Server", options=server_opts)

log_view = df.copy()
if selected_server != "All":
    log_view = log_view[log_view["server_name"] == selected_server]

search_term = st.text_input("Search ticket ID / category", placeholder="e.g. TKT1001 or Network")
if search_term:
    mask = (
        log_view["ticket_id"].str.contains(search_term, case=False, na=False)
        | log_view["ticket_category"].str.contains(search_term, case=False, na=False)
    )
    log_view = log_view[mask]

display_cols = [
    "timestamp", "server_name", "region", "status",
    "uptime_hours", "downtime_minutes",
    "ticket_id", "ticket_category", "ticket_resolution_time_mins",
    "cpu_usage_pct", "memory_usage_pct", "disk_usage_pct",
    "network_bandwidth_mbps",
]

def colour_status(val):
    colours = {"Critical": "background-color:#7f1d1d;color:#fca5a5",
                "Warning": "background-color:#78350f;color:#fde68a",
                "Resolved": "background-color:#14532d;color:#86efac"}
    return colours.get(val, "")

styled = log_view[display_cols].style.applymap(colour_status, subset=["status"])
st.dataframe(styled, use_container_width=True, height=400)

st.caption(f"Showing {len(log_view)} rows")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    """
    <div style='text-align:center;opacity:0.6;font-size:0.8rem'>
    🖥️ <b>IT Operations Analytics Dashboard</b> · Built with Streamlit & Plotly
    · Role: IT &amp; Web Support Specialist · Nationality: Pakistani
    </div>
    """,
    unsafe_allow_html=True,
)
