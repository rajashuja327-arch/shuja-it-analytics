# 🖥️ IT Operations Analytics Dashboard

> **Role:** IT & Web Support Specialist  
> **Nationality:** Pakistani | **Status:** Active Portfolio Project

An end-to-end Python web application that ingests IT operations log data, performs analytical processing, and renders an interactive dashboard — deployable to [Streamlit Community Cloud](https://streamlit.io/cloud) in minutes.

---

## 📐 Architecture

```
shuja-it-analytics/
│
├── data/
│   └── it_operations_log.csv   ← Raw IT metrics dataset
│
├── analytics.py                ← Data processing & analytics engine
├── app.py                      ← Streamlit web application (UI layer)
├── requirements.txt            ← Python dependencies
└── README.md                   ← This file
```

### Data Flow

```
CSV Dataset
    │
    ▼
analytics.py  ──  load_data()       → Raw DataFrame
              ──  clean_data()      → Imputes missing values
              ──  compute_kpis()    → Top-level KPI dict
              ──  compute_efficiency_scores() → Per-server scores
              ──  ticket_category_analysis()  → Ticket breakdown
              ──  daily_metrics()   → Time-series aggregations
    │
    ▼
app.py  (Streamlit)
    ├── KPI Cards (6 metrics)
    ├── Efficiency Score Bar Chart
    ├── Status Distribution Pie
    ├── Daily Trend Subplots (4-panel)
    ├── Ticket Category Charts
    ├── CPU × Region Heatmap
    ├── CPU vs Memory Scatter
    ├── Summary Statistics Table
    └── Filterable Log Viewer
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **KPI Cards** | Avg uptime %, resolution time, bandwidth, critical/warning counts |
| **Efficiency Scores** | Composite 0-100 score per server (uptime, resolution, CPU, memory, bandwidth) |
| **Interactive Filters** | Sidebar filter by region & server status |
| **Trend Charts** | 4-panel daily trend: CPU, Memory, Bandwidth, Downtime |
| **Ticket Analytics** | Category counts & avg resolution time |
| **Heatmap** | CPU % across server × region grid |
| **Scatter Plot** | CPU vs Memory with bubble size = bandwidth |
| **Log Viewer** | Searchable, colour-coded status table |

---

## 🚀 Local Setup & Run

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/shuja-it-analytics.git
cd shuja-it-analytics

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The browser will open automatically at **http://localhost:8501**.

---

## ☁️ Deployment Guide

### Option A — Streamlit Community Cloud (Recommended, Free)

1. Push this repository to a **public** GitHub repo.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) → **New app**.
3. Select your repo, branch (`main`), and set **Main file path** to `app.py`.
4. Click **Deploy** — live URL generated in ~60 seconds.

### Option B — Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Add a `vercel.json`:
```json
{
  "builds": [{ "src": "app.py", "use": "@vercel/python" }],
  "routes": [{ "src": "/(.*)", "dest": "app.py" }]
}
```
3. Run `vercel --prod` in the project directory.

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | ≥1.35 | Web UI framework |
| `pandas` | ≥2.1 | Data loading & processing |
| `numpy` | ≥1.26 | Numerical computation |
| `plotly` | ≥5.20 | Interactive charts |

---

## 📊 Dataset Schema

| Column | Type | Description |
|---|---|---|
| `timestamp` | datetime | Log entry timestamp |
| `server_id` | string | Server identifier |
| `server_name` | string | Human-readable server name |
| `uptime_hours` | float | Hours server was up in period |
| `downtime_minutes` | float | Minutes of downtime (0 if none) |
| `ticket_id` | string | Support ticket ID (nullable) |
| `ticket_category` | string | Network / Hardware / Software |
| `ticket_resolution_time_mins` | float | Minutes to resolve ticket |
| `network_bandwidth_mbps` | float | Average bandwidth in Mbps |
| `cpu_usage_pct` | float | CPU utilisation % |
| `memory_usage_pct` | float | Memory utilisation % |
| `disk_usage_pct` | float | Disk utilisation % |
| `region` | string | North / South / East / West |
| `status` | string | Resolved / Warning / Critical |

---

## 🔧 Efficiency Score Formula

$$\text{Score} = 0.35 \times \text{Uptime} + 0.25 \times \text{Resolution} + 0.20 \times \text{CPU} + 0.10 \times \text{Memory} + 0.10 \times \text{Bandwidth}$$

All sub-scores are normalised to **0–100** (higher = better).

---

## 👤 About

Built as a live portfolio project demonstrating:
- **Python data engineering** (Pandas, NumPy)
- **Interactive web development** (Streamlit, Plotly)
- **IT operations analytics** and KPI dashboarding
- **Cloud deployment** readiness

> Courses: *Data Science Essentials with Python* | *IT Systems & Web Administration*
