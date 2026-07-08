# PJM Hourly Energy Load — Time Series Analysis

Exploratory time series analysis on the **PJM Hourly Energy Consumption** dataset (regional US power grid load data, 1998–2018, source: [Kaggle](https://www.kaggle.com/datasets/robikscube/hourly-energy-consumption)). Covers trend and seasonality visualization, 12-month moving averages, monthly seasonal decomposition, stationarity testing (raw vs. first-differenced), and missing-value imputation comparison (rolling average vs. forward-fill/mean).

Coursework project — MS Data Science, Time Series Analysis course, UET Lahore.

---

## Dataset Overview

12 regional utility files + 1 combined estimate file, all with hourly `Datetime` + `MW` (megawatt load) columns.

| File | Rows | Date Range | Missing Values | Duplicate Timestamps |
|---|---|---|---|---|
| AEP_hourly.csv | 121,273 | 2004-10-01 → 2018-08-03 | 0 | 4 |
| COMED_hourly.csv | 66,497 | 2011-01-01 → 2018-08-03 | 0 | 4 |
| DAYTON_hourly.csv | 121,275 | 2004-10-01 → 2018-08-03 | 0 | 4 |
| DEOK_hourly.csv | 57,739 | 2012-01-01 → 2018-08-03 | 0 | 4 |
| DOM_hourly.csv | 116,189 | 2005-05-01 → 2018-08-03 | 0 | 4 |
| DUQ_hourly.csv | 119,068 | 2005-01-01 → 2018-08-03 | 0 | 4 |
| EKPC_hourly.csv | 45,334 | 2013-06-01 → 2018-08-03 | 0 | 4 |
| FE_hourly.csv | 62,874 | 2011-06-01 → 2018-08-03 | 0 | 4 |
| NI_hourly.csv | 58,450 | 2004-05-01 → 2011-01-01 | 0 | 0 |
| PJME_hourly.csv | 145,366 | 2002-01-01 → 2018-08-03 | 0 | 4 |
| PJMW_hourly.csv | 143,206 | 2002-04-01 → 2018-08-03 | 0 | 4 |
| **PJM_Load_hourly.csv** | 32,896 | 1998-04-01 → 2002-01-01 | 0 | 0 |
| pjm_hourly_est.csv (combined) | 178,262 | 1998-04-01 → 2018-08-03 | ~1.05M (sparse combined format) | 4 |

> **Note:** Individual regional files (AEP, COMED, DAYTON, etc.) have zero missing values in their raw form — each is a clean, standalone series. The combined `pjm_hourly_est.csv` file has many missing values *by design*, since each row only has data for the regions active at that timestamp. The assignment specifically asks for the **PJM_Load_hourly.csv** file — that is the primary dataset for Assignment 1 and Task 2 below. The other 11 regional files were run through the same pipeline for practice/portfolio purposes but are not required by the assignment.

All 13 files were validated with `check_all_datasets.py` — loaded successfully, checked for row counts, date ranges, missing values, duplicate timestamps, and per-column min/max/mean.

---

## Assignment 1 — Trend, Seasonality, Moving Average

For each region:
1. Resampled to monthly mean to visualize the overall trend
2. Plotted a 12-month moving average over the monthly series
3. Built monthly boxplots to examine seasonality
4. Ran additive seasonal decomposition (trend / seasonal / residual)
5. Auto-generated a short conclusion identifying peak/trough months

**Outputs per region** (in `plots/<REGION>/`):
- `01_trend.png` — monthly mean trend
- `02_moving_average.png` — 12-month moving average overlay
- `03_monthly_boxplot.png` — seasonality boxplots
- `04_seasonal_decomposition.png` — trend/seasonal/residual breakdown

## Task 2 — Stationarity & Imputation

For each region:
1. Plotted raw hourly series (first 2000 hours) vs. first-differenced series
2. Ran Augmented Dickey-Fuller (ADF) test on raw vs. differenced data
3. Simulated missing gaps and compared two imputation methods: rolling (24-hr window) average vs. forward-fill + mean fallback

**Outputs per region:**
- `05_raw_series.png`
- `06_differenced_series.png`
- `07_imputation_comparison.png`

**Full written conclusions for every region** are in [`conclusions.md`](conclusions.md), auto-generated from the actual ADF statistics and seasonal peak/trough detection — not placeholder text.

---

## How to Run

```bash
pip install pandas matplotlib statsmodels --break-system-packages

# 1. Validate all 13 files (shape, missing values, duplicates, stats)
python3 check_all_datasets.py

# 2. Run full Assignment 1 + Task 2 pipeline on all regions
python3 time_series_analysis.py
```

Results land in `outputs/plots/<REGION>/` and `outputs/conclusions.md`.

---

## Files in This Repo

```
├── README.md
├── check_all_datasets.py       # dataset validation script
├── time_series_analysis.py     # full analysis pipeline (Assignment 1 + Task 2)
├── conclusions.md              # auto-generated written conclusions, all regions
└── plots/
    └── <REGION>/                # 01_trend.png ... 07_imputation_comparison.png
```

## Key Finding (PJM_Load, the assignment's primary dataset)

ADF test on the raw series is already stationary (p < 0.05) at the hourly resolution — common for load data with strong daily/weekly cycles rather than a long-term trend. First-differencing pushes the ADF statistic even further from the critical value, confirming the differenced series has no unit root and is well-suited for classical models (ARIMA/SARIMA) that assume stationarity.
