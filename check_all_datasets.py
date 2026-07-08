"""
PJM Hourly Energy Consumption — Dataset Check Script
Runs basic validation + EDA on all 13 CSV files in the dataset.
"""

import pandas as pd
import os

DATA_DIR = "pjm_data"
FILES = [
    "AEP_hourly.csv", "COMED_hourly.csv", "DAYTON_hourly.csv",
    "DEOK_hourly.csv", "DOM_hourly.csv", "DUQ_hourly.csv",
    "EKPC_hourly.csv", "FE_hourly.csv", "NI_hourly.csv",
    "PJME_hourly.csv", "PJMW_hourly.csv", "PJM_Load_hourly.csv",
    "pjm_hourly_est.csv"
]

def check_file(filename):
    path = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(path, parse_dates=["Datetime"])

    report = {
        "file": filename,
        "rows": len(df),
        "columns": list(df.columns),
        "date_min": df["Datetime"].min(),
        "date_max": df["Datetime"].max(),
        "missing_values": df.isna().sum().sum(),
        "duplicate_datetimes": df["Datetime"].duplicated().sum(),
        "value_col_stats": {}
    }

    value_cols = [c for c in df.columns if c != "Datetime"]
    for col in value_cols:
        report["value_col_stats"][col] = {
            "min": df[col].min(),
            "max": df[col].max(),
            "mean": round(df[col].mean(), 2) if df[col].notna().any() else None,
            "missing": df[col].isna().sum()
        }

    return report


def main():
    print("=" * 70)
    print("PJM HOURLY ENERGY CONSUMPTION — DATASET CHECK")
    print("=" * 70)

    all_reports = []
    for f in FILES:
        try:
            r = check_file(f)
            all_reports.append(r)
            print(f"\n[OK] {r['file']}")
            print(f"  Rows           : {r['rows']:,}")
            print(f"  Date range     : {r['date_min']}  ->  {r['date_max']}")
            print(f"  Missing values : {r['missing_values']}")
            print(f"  Duplicate rows : {r['duplicate_datetimes']}")
            for col, stats in r["value_col_stats"].items():
                print(f"  {col:12s} min={stats['min']}  max={stats['max']}  "
                      f"mean={stats['mean']}  missing={stats['missing']}")
        except Exception as e:
            print(f"\n[FAIL] {f} -> {e}")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(all_reports)}/{len(FILES)} files loaded successfully")
    print("=" * 70)

    return all_reports


if __name__ == "__main__":
    main()
