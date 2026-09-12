"""
analytics.py — IT Operations Analytics Backend
Reads the IT operations log CSV, cleans data, computes KPIs and efficiency scores.
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path("data") / "it_operations_log.csv"


def load_data(path=DATA_PATH):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df.columns = df.columns.str.strip()
    return df


def clean_data(df):
    df = df.copy()
    df["ticket_resolution_time_mins"] = df.groupby("ticket_category")[
        "ticket_resolution_time_mins"
    ].transform(lambda s: s.fillna(s.median()))
    overall_med = df["ticket_resolution_time_mins"].median()
    df["ticket_resolution_time_mins"] = df["ticket_resolution_time_mins"].fillna(overall_med)
    df["ticket_id"] = df["ticket_id"].fillna("UNTRACKED")
    df["downtime_minutes"] = df["downtime_minutes"].fillna(0)
    return df


def compute_kpis(df):
    avg_uptime_pct = (
        df["uptime_hours"] / (df["uptime_hours"] + df["downtime_minutes"] / 60) * 100
    ).mean()
    return {
        "total_records": len(df),
        "avg_uptime_pct": round(avg_uptime_pct, 2),
        "avg_resolution_mins": round(df["ticket_resolution_time_mins"].mean(), 1),
        "avg_bandwidth_mbps": round(df["network_bandwidth_mbps"].mean(), 1),
        "avg_cpu_pct": round(df["cpu_usage_pct"].mean(), 2),
        "avg_memory_pct": round(df["memory_usage_pct"].mean(), 2),
        "avg_disk_pct": round(df["disk_usage_pct"].mean(), 2),
        "critical_count": int((df["status"] == "Critical").sum()),
        "warning_count": int((df["status"] == "Warning").sum()),
        "resolved_count": int((df["status"] == "Resolved").sum()),
        "total_downtime_hrs": round(df["downtime_minutes"].sum() / 60, 2),
    }


def compute_efficiency_scores(df):
    grp = df.groupby("server_name").agg(
        uptime_pct=(
            "uptime_hours",
            lambda x: (x / (x + df.loc[x.index, "downtime_minutes"] / 60)).mean() * 100,
        ),
        avg_resolution=("ticket_resolution_time_mins", "mean"),
        avg_cpu=("cpu_usage_pct", "mean"),
        avg_memory=("memory_usage_pct", "mean"),
        avg_bandwidth=("network_bandwidth_mbps", "mean"),
    ).reset_index()

    grp["uptime_score"] = grp["uptime_pct"].clip(0, 100)
    max_res = grp["avg_resolution"].max()
    grp["resolution_score"] = (1 - grp["avg_resolution"] / max_res) * 100
    grp["cpu_score"] = (100 - grp["avg_cpu"]).clip(0, 100)
    grp["memory_score"] = (100 - grp["avg_memory"]).clip(0, 100)
    min_bw, max_bw = grp["avg_bandwidth"].min(), grp["avg_bandwidth"].max()
    if max_bw > min_bw:
        grp["bandwidth_score"] = (grp["avg_bandwidth"] - min_bw) / (max_bw - min_bw) * 100
    else:
        grp["bandwidth_score"] = 100.0

    grp["efficiency_score"] = (
        0.35 * grp["uptime_score"]
        + 0.25 * grp["resolution_score"]
        + 0.20 * grp["cpu_score"]
        + 0.10 * grp["memory_score"]
        + 0.10 * grp["bandwidth_score"]
    ).round(1)

    return grp[["server_name", "uptime_pct", "avg_resolution", "avg_cpu",
                "avg_memory", "avg_bandwidth", "efficiency_score"]].sort_values(
        "efficiency_score", ascending=False
    )


def summary_statistics(df):
    cols = [
        "uptime_hours", "downtime_minutes", "ticket_resolution_time_mins",
        "network_bandwidth_mbps", "cpu_usage_pct", "memory_usage_pct", "disk_usage_pct",
    ]
    return df[cols].describe().round(2)


def ticket_category_analysis(df):
    return (
        df[df["ticket_id"] != "UNTRACKED"]
        .groupby("ticket_category")
        .agg(
            ticket_count=("ticket_id", "count"),
            avg_resolution_mins=("ticket_resolution_time_mins", "mean"),
            max_resolution_mins=("ticket_resolution_time_mins", "max"),
        )
        .round(1)
        .reset_index()
        .sort_values("avg_resolution_mins", ascending=False)
    )


def daily_metrics(df):
    df2 = df.copy()
    df2["date"] = df2["timestamp"].dt.date
    return (
        df2.groupby("date")
        .agg(
            avg_cpu=("cpu_usage_pct", "mean"),
            avg_memory=("memory_usage_pct", "mean"),
            avg_bandwidth=("network_bandwidth_mbps", "mean"),
            total_downtime_mins=("downtime_minutes", "sum"),
            avg_resolution=("ticket_resolution_time_mins", "mean"),
        )
        .round(2)
        .reset_index()
    )
