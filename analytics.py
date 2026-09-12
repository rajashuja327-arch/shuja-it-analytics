"""
analytics.py — IT Operations Analytics Backend
Reads the IT operations log CSV, cleans data, computes KPIs and efficiency scores.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── Path resolution ────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "it_operations_log.csv"


# ── Data Loading & Cleaning ────────────────────────────────────────────────────
def load_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
   def load_data(path: str = None) -> pd.DataFrame:
  import os
    base_dir = os.path.dirname(os.path.abspath(_file_))
    file_path = os.path.join(base_dir, 'data', 'it_operations_log.csv')
    if not os.path.exists(file_path):
        file_path = 'it_operations_log.csv'
    df = pd.read_csv(file_path, parse_dates=["timestamp"])
    df.columns = df.columns.str.strip()
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean missing values:
    - ticket_resolution_time_mins: fill with median per ticket category
    - ticket_id: fill missing with 'UNTRACKED'
    - downtime_minutes: fill missing with 0
    """
    df = df.copy()

    # Fill missing resolution times with per-category median
    df["ticket_resolution_time_mins"] = df.groupby("ticket_category")[
        "ticket_resolution_time_mins"
    ].transform(lambda s: s.fillna(s.median()))

    # Remaining nulls (categories with all-null) → overall median
    overall_med = df["ticket_resolution_time_mins"].median()
    df["ticket_resolution_time_mins"] = df["ticket_resolution_time_mins"].fillna(
        overall_med
    )

    df["ticket_id"] = df["ticket_id"].fillna("UNTRACKED")
    df["downtime_minutes"] = df["downtime_minutes"].fillna(0)

    return df


# ── KPI Computations ───────────────────────────────────────────────────────────
def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a dictionary of top-level KPIs."""
    total_records = len(df)
    avg_uptime_pct = (
        df["uptime_hours"] / (df["uptime_hours"] + df["downtime_minutes"] / 60) * 100
    ).mean()
    avg_resolution_mins = df["ticket_resolution_time_mins"].mean()
    avg_bandwidth_mbps = df["network_bandwidth_mbps"].mean()
    avg_cpu = df["cpu_usage_pct"].mean()
    avg_memory = df["memory_usage_pct"].mean()
    avg_disk = df["disk_usage_pct"].mean()

    critical_count = (df["status"] == "Critical").sum()
    warning_count = (df["status"] == "Warning").sum()
    resolved_count = (df["status"] == "Resolved").sum()

    total_downtime_hrs = df["downtime_minutes"].sum() / 60

    return {
        "total_records": total_records,
        "avg_uptime_pct": round(avg_uptime_pct, 2),
        "avg_resolution_mins": round(avg_resolution_mins, 1),
        "avg_bandwidth_mbps": round(avg_bandwidth_mbps, 1),
        "avg_cpu_pct": round(avg_cpu, 2),
        "avg_memory_pct": round(avg_memory, 2),
        "avg_disk_pct": round(avg_disk, 2),
        "critical_count": int(critical_count),
        "warning_count": int(warning_count),
        "resolved_count": int(resolved_count),
        "total_downtime_hrs": round(total_downtime_hrs, 2),
    }


# ── Efficiency Score ───────────────────────────────────────────────────────────
def compute_efficiency_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute a composite System Efficiency Score (0–100) per server.

    Score = 0.35*uptime_score + 0.25*resolution_score + 0.20*cpu_score
            + 0.10*memory_score + 0.10*bandwidth_score
    """
    grp = df.groupby("server_name").agg(
        uptime_pct=(
            "uptime_hours",
            lambda x: (
                x / (x + df.loc[x.index, "downtime_minutes"] / 60)
            ).mean()
            * 100,
        ),
        avg_resolution=("ticket_resolution_time_mins", "mean"),
        avg_cpu=("cpu_usage_pct", "mean"),
        avg_memory=("memory_usage_pct", "mean"),
        avg_bandwidth=("network_bandwidth_mbps", "mean"),
    ).reset_index()

    # Normalise each metric to 0-100 (higher = better)
    grp["uptime_score"] = grp["uptime_pct"].clip(0, 100)

    max_res = grp["avg_resolution"].max()
    grp["resolution_score"] = (1 - grp["avg_resolution"] / max_res) * 100

    grp["cpu_score"] = (100 - grp["avg_cpu"]).clip(0, 100)
    grp["memory_score"] = (100 - grp["avg_memory"]).clip(0, 100)

    min_bw, max_bw = grp["avg_bandwidth"].min(), grp["avg_bandwidth"].max()
    if max_bw > min_bw:
        grp["bandwidth_score"] = (
            (grp["avg_bandwidth"] - min_bw) / (max_bw - min_bw) * 100
        )
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


# ── Summary Statistics ─────────────────────────────────────────────────────────
def summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return describe() on key numeric columns."""
    cols = [
        "uptime_hours", "downtime_minutes", "ticket_resolution_time_mins",
        "network_bandwidth_mbps", "cpu_usage_pct", "memory_usage_pct", "disk_usage_pct",
    ]
    return df[cols].describe().round(2)


# ── Ticket Analysis ────────────────────────────────────────────────────────────
def ticket_category_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Avg resolution time and count by ticket category."""
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


# ── Time-Series Data ───────────────────────────────────────────────────────────
def daily_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate metrics by date."""
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


# ── Quick self-test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    raw = load_data()
    df_clean = clean_data(raw)

    print("=== KPIs ===")
    for k, v in compute_kpis(df_clean).items():
        print(f"  {k}: {v}")

    print("\n=== Efficiency Scores ===")
    print(compute_efficiency_scores(df_clean).to_string(index=False))

    print("\n=== Ticket Category Analysis ===")
    print(ticket_category_analysis(df_clean).to_string(index=False))
