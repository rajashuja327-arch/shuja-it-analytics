"""
analytics.py — IT Operations Analytics Backend
Auto-generates sample data if CSV is not found (Streamlit Cloud compatible).
"""

import io
import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path("data") / "it_operations_log.csv"

SAMPLE_CSV = """timestamp,server_id,server_name,uptime_hours,downtime_minutes,ticket_id,ticket_category,ticket_resolution_time_mins,network_bandwidth_mbps,cpu_usage_pct,memory_usage_pct,disk_usage_pct,region,status
2024-01-01 08:00,SRV001,WebServer-01,720,0,TKT1001,Network,15,850,45.2,62.1,55.3,North,Resolved
2024-01-01 09:00,SRV002,DBServer-01,720,5,TKT1002,Software,30,620,78.5,88.4,72.1,North,Resolved
2024-01-01 10:00,SRV003,AppServer-01,718,12,TKT1003,Hardware,90,430,55.3,70.2,60.8,South,Resolved
2024-01-01 11:00,SRV004,WebServer-02,720,0,TKT1004,Network,10,920,30.1,45.6,40.2,East,Resolved
2024-01-01 12:00,SRV005,FileServer-01,715,30,,Network,,780,90.2,95.1,88.4,West,Critical
2024-01-02 08:00,SRV001,WebServer-01,744,0,TKT1005,Software,20,870,42.8,60.5,56.1,North,Resolved
2024-01-02 09:00,SRV002,DBServer-01,740,10,TKT1006,Hardware,120,590,82.3,91.2,75.6,North,Resolved
2024-01-02 10:00,SRV003,AppServer-01,744,0,TKT1007,Network,8,460,50.1,65.3,58.9,South,Resolved
2024-01-02 11:00,SRV004,WebServer-02,744,0,TKT1008,Software,45,890,28.7,43.2,38.7,East,Resolved
2024-01-02 12:00,SRV005,FileServer-01,738,15,TKT1009,Hardware,200,800,88.1,92.4,85.3,West,Resolved
2024-01-03 08:00,SRV001,WebServer-01,720,5,TKT1010,Network,12,840,48.5,63.7,57.2,North,Resolved
2024-01-03 09:00,SRV002,DBServer-01,716,25,,Hardware,,605,76.9,87.8,74.0,North,Critical
2024-01-03 10:00,SRV003,AppServer-01,720,0,TKT1011,Software,60,445,53.8,68.5,62.1,South,Resolved
2024-01-03 11:00,SRV004,WebServer-02,720,0,TKT1012,Network,9,905,32.4,47.1,41.5,East,Resolved
2024-01-03 12:00,SRV005,FileServer-01,718,10,TKT1013,Software,35,815,85.6,90.3,83.7,West,Resolved
2024-01-04 08:00,SRV001,WebServer-01,744,0,TKT1014,Hardware,180,855,44.1,61.8,54.9,North,Resolved
2024-01-04 09:00,SRV002,DBServer-01,744,0,TKT1015,Network,15,630,80.2,89.7,73.4,North,Resolved
2024-01-04 10:00,SRV003,AppServer-01,740,20,TKT1016,Network,22,455,57.2,71.4,63.5,South,Resolved
2024-01-04 11:00,SRV004,WebServer-02,744,0,TKT1017,Software,55,915,29.8,44.8,39.6,East,Resolved
2024-01-04 12:00,SRV005,FileServer-01,744,0,TKT1018,Hardware,95,825,87.3,93.1,86.2,West,Resolved
2024-01-05 08:00,SRV001,WebServer-01,720,0,TKT1019,Software,18,860,43.5,62.4,55.8,North,Resolved
2024-01-05 09:00,SRV002,DBServer-01,720,0,TKT1020,Network,11,610,79.8,88.9,72.8,North,Resolved
2024-01-05 10:00,SRV003,AppServer-01,720,0,TKT1021,Hardware,150,470,52.6,67.1,61.4,South,Resolved
2024-01-05 11:00,SRV004,WebServer-02,718,12,,Software,,900,31.5,46.3,40.9,East,Warning
2024-01-05 12:00,SRV005,FileServer-01,720,0,TKT1022,Network,7,810,84.9,91.6,84.8,West,Resolved
2024-01-06 08:00,SRV001,WebServer-01,744,0,TKT1023,Hardware,220,865,47.2,64.0,57.6,North,Resolved
2024-01-06 09:00,SRV002,DBServer-01,740,8,TKT1024,Software,40,625,81.7,90.5,74.2,North,Resolved
2024-01-06 10:00,SRV003,AppServer-01,744,0,TKT1025,Network,13,450,54.9,69.8,62.7,South,Resolved
2024-01-06 11:00,SRV004,WebServer-02,744,0,TKT1026,Network,16,910,30.7,45.0,40.1,East,Resolved
2024-01-06 12:00,SRV005,FileServer-01,736,20,TKT1027,Hardware,110,820,86.8,92.7,85.9,West,Resolved
2024-01-07 08:00,SRV001,WebServer-01,720,0,TKT1028,Software,25,845,41.9,60.2,54.6,North,Resolved
2024-01-07 09:00,SRV002,DBServer-01,720,0,TKT1029,Network,9,615,77.4,87.3,71.9,North,Resolved
2024-01-07 10:00,SRV003,AppServer-01,720,3,TKT1030,Software,70,440,56.1,70.7,63.0,South,Resolved
2024-01-07 11:00,SRV004,WebServer-02,720,0,TKT1031,Hardware,130,925,33.2,48.4,42.3,East,Resolved
2024-01-07 12:00,SRV005,FileServer-01,720,0,TKT1032,Network,6,800,83.5,90.9,84.1,West,Resolved
2024-01-08 08:00,SRV001,WebServer-01,744,0,TKT1033,Network,14,875,46.8,63.3,56.7,North,Resolved
2024-01-08 09:00,SRV002,DBServer-01,741,18,TKT1034,Hardware,160,640,83.1,91.8,75.0,North,Resolved
2024-01-08 10:00,SRV003,AppServer-01,744,0,TKT1035,Network,11,465,51.8,66.7,60.2,South,Resolved
2024-01-08 11:00,SRV004,WebServer-02,744,0,TKT1036,Software,42,895,28.3,42.9,38.3,East,Resolved
2024-01-08 12:00,SRV005,FileServer-01,744,0,TKT1037,Hardware,85,830,86.0,91.3,83.5,West,Resolved
2024-01-09 08:00,SRV001,WebServer-01,720,2,TKT1038,Software,33,852,44.7,61.6,55.5,North,Resolved
2024-01-09 09:00,SRV002,DBServer-01,715,30,TKT1039,Network,19,618,80.5,89.2,73.7,North,Resolved
2024-01-09 10:00,SRV003,AppServer-01,720,0,TKT1040,Hardware,100,458,55.5,69.1,62.4,South,Resolved
2024-01-09 11:00,SRV004,WebServer-02,720,0,TKT1041,Network,8,908,31.9,46.7,41.1,East,Resolved
2024-01-09 12:00,SRV005,FileServer-01,716,22,,Software,,812,88.8,93.9,86.8,West,Critical
2024-01-10 08:00,SRV001,WebServer-01,744,0,TKT1042,Hardware,190,848,43.2,61.0,54.3,North,Resolved
2024-01-10 09:00,SRV002,DBServer-01,744,0,TKT1043,Software,28,628,78.1,88.1,72.5,North,Resolved
2024-01-10 10:00,SRV003,AppServer-01,742,10,TKT1044,Network,10,462,53.2,68.0,61.8,South,Resolved
2024-01-10 11:00,SRV004,WebServer-02,744,0,TKT1045,Software,38,918,30.3,45.4,40.5,East,Resolved
2024-01-10 12:00,SRV005,FileServer-01,744,0,TKT1046,Network,5,808,85.2,91.0,84.5,West,Resolved"""


def load_data(path=DATA_PATH):
    """Load CSV — falls back to embedded data if file not found."""
    try:
        df = pd.read_csv(path, parse_dates=["timestamp"])
    except FileNotFoundError:
        df = pd.read_csv(io.StringIO(SAMPLE_CSV), parse_dates=["timestamp"])
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
