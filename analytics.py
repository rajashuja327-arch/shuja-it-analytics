
import os
import pandas as pd

def load_data(path: str = None) -> pd.DataFrame:
    base_dir = os.path.dirname(os.path.abspath(_file_))
    file_path = os.path.join(base_dir, 'data', 'it_operations_log.csv')
    if not os.path.exists(file_path):
        file_path = 'it_operations_log.csv'
    df = pd.read_csv(file_path, parse_dates=["timestamp"])
    df.columns = df.columns.str.strip()
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'ticket_resolution_time_mins' in df.columns:
        median_val = df['ticket_resolution_time_mins'].median()
        df['ticket_resolution_time_mins'] = df['ticket_resolution_time_mins'].fillna(median_val)
    if 'ticket_id' in df.columns:
        df['ticket_id'] = df['ticket_id'].fillna('UNTRACKED')
    return df

def compute_kpis(df: pd.DataFrame) -> dict:
    total_logs = len(df)
    critical_events = len(df[df['severity'] == 'Critical']) if 'severity' in df.columns else 0
    avg_resolution = df['ticket_resolution_time_mins'].mean() if 'ticket_resolution_time_mins' in df.columns else 0
    sla_breaches = len(df[df['sla_status'] == 'Breached']) if 'sla_status' in df.columns else 0
    
    return {
        "total_logs": total_logs,
        "critical_events": critical_events,
        "avg_resolution": round(avg_resolution, 2),
        "sla_breaches": sla_breaches
    }
