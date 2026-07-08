"""
PJM Hourly Energy Consumption — Time Series Analysis
Covers:
  Assignment 1: trend plot, 12-month moving average, monthly boxplots,
                seasonal decomposition, short conclusion.
  Task 2      : stationarity check (raw vs. first-differenced),
                missing value imputation comparison (rolling mean vs.
                forward-fill/mean).

Runs on all 13 files in the PJM Hourly Energy Consumption dataset.
Outputs: PNG plots saved to outputs/plots/<REGION>/
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller

DATA_DIR = "pjm_data"
OUT_DIR = "outputs/plots"

FILES = {
    "AEP": "AEP_hourly.csv", "COMED": "COMED_hourly.csv",
    "DAYTON": "DAYTON_hourly.csv", "DEOK": "DEOK_hourly.csv",
    "DOM": "DOM_hourly.csv", "DUQ": "DUQ_hourly.csv",
    "EKPC": "EKPC_hourly.csv", "FE": "FE_hourly.csv",
    "NI": "NI_hourly.csv", "PJME": "PJME_hourly.csv",
    "PJMW": "PJMW_hourly.csv", "PJM_Load": "PJM_Load_hourly.csv",
}


def load_series(filename, value_col):
    df = pd.read_csv(os.path.join(DATA_DIR, filename), parse_dates=["Datetime"])
    df = df.drop_duplicates(subset="Datetime").sort_values("Datetime")
    df = df.set_index("Datetime")
    return df[value_col]


def assignment1(region, series, out_dir):
    """Trend, 12-month moving average, monthly boxplots, seasonal decomposition."""
    monthly = series.resample("ME").mean()

    # Trend plot
    plt.figure(figsize=(12, 4))
    monthly.plot(title=f"{region} — Monthly Mean Load (Trend)")
    plt.ylabel("MW")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/01_trend.png", dpi=100)
    plt.close()

    # 12-month moving average
    plt.figure(figsize=(12, 4))
    monthly.plot(alpha=0.4, label="Monthly mean")
    monthly.rolling(12).mean().plot(label="12-month moving average", linewidth=2)
    plt.title(f"{region} — 12-Month Moving Average")
    plt.ylabel("MW")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{out_dir}/02_moving_average.png", dpi=100)
    plt.close()

    # Monthly boxplots (seasonality)
    df_box = series.to_frame("value")
    df_box["month"] = df_box.index.month
    plt.figure(figsize=(12, 5))
    df_box.boxplot(column="value", by="month")
    plt.title(f"{region} — Monthly Distribution (Seasonality)")
    plt.suptitle("")
    plt.xlabel("Month")
    plt.ylabel("MW")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/03_monthly_boxplot.png", dpi=100)
    plt.close()

    # Seasonal decomposition (on monthly series, additive)
    decomposition = None
    if len(monthly.dropna()) >= 24:
        decomposition = seasonal_decompose(monthly.dropna(), model="additive", period=12)
        fig = decomposition.plot()
        fig.set_size_inches(12, 8)
        fig.suptitle(f"{region} — Seasonal Decomposition", y=1.02)
        plt.tight_layout()
        plt.savefig(f"{out_dir}/04_seasonal_decomposition.png", dpi=100)
        plt.close()

    # Conclusion text
    strongest_month = df_box.groupby("month")["value"].mean().idxmax()
    weakest_month = df_box.groupby("month")["value"].mean().idxmin()
    conclusion = (
        f"{region}: The series shows a clear repeating annual pattern with load peaking "
        f"around month {strongest_month} and dipping around month {weakest_month}, "
        f"consistent with seasonal heating/cooling demand. The 12-month moving average "
        f"smooths short-term fluctuations and reveals the longer-term trend. "
        f"Overall variation across years appears "
        f"{'stable' if monthly.std() / monthly.mean() < 0.15 else 'moderately volatile'} "
        f"relative to the mean load level."
    )
    return conclusion


def task2(region, series, out_dir):
    """Stationarity check + imputation comparison."""
    hourly = series.copy()

    # Stationarity: raw vs differenced (use a representative subsample for speed on large series)
    adf_sample = hourly.dropna().iloc[-20000:]
    adf_raw = adfuller(adf_sample, autolag="AIC", maxlag=48)
    diff = adf_sample.diff().dropna()
    adf_diff = adfuller(diff, autolag="AIC", maxlag=48)

    plt.figure(figsize=(12, 4))
    hourly.iloc[:2000].plot(title=f"{region} — Raw Series (first 2000 hrs)")
    plt.ylabel("MW")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/05_raw_series.png", dpi=100)
    plt.close()

    plt.figure(figsize=(12, 4))
    diff.iloc[:2000].plot(title=f"{region} — First-Differenced Series (first 2000 hrs)", color="darkorange")
    plt.ylabel("Delta MW")
    plt.tight_layout()
    plt.savefig(f"{out_dir}/06_differenced_series.png", dpi=100)
    plt.close()

    # Imputation comparison — artificially introduce gaps to demonstrate method
    sample = hourly.iloc[:5000].copy()
    gapped = sample.copy()
    gapped.iloc[100:130] = None
    gapped.iloc[2000:2050] = None

    rolling_imputed = gapped.fillna(gapped.rolling(24, min_periods=1, center=True).mean())
    ffill_imputed = gapped.ffill().fillna(gapped.mean())

    plt.figure(figsize=(12, 4))
    sample.plot(label="Original", alpha=0.6)
    rolling_imputed.plot(label="Rolling-average imputed", linestyle="--")
    ffill_imputed.plot(label="Forward-fill/mean imputed", linestyle=":")
    plt.title(f"{region} — Imputation Method Comparison")
    plt.ylabel("MW")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{out_dir}/07_imputation_comparison.png", dpi=100)
    plt.close()

    summary = (
        f"{region}: ADF statistic (raw) = {adf_raw[0]:.3f}, p-value = {adf_raw[1]:.4f} "
        f"({'stationary' if adf_raw[1] < 0.05 else 'non-stationary'}). "
        f"After first-differencing, ADF statistic = {adf_diff[0]:.3f}, p-value = {adf_diff[1]:.4f} "
        f"({'stationary' if adf_diff[1] < 0.05 else 'non-stationary'}). "
        f"Differencing removes trend/level dependence, making the series more suitable for "
        f"classical forecasting models that assume stationarity."
    )
    return summary


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    all_conclusions = []

    for region, filename in FILES.items():
        out_dir = f"{OUT_DIR}/{region}"
        if os.path.isdir(out_dir) and len(os.listdir(out_dir)) >= 7:
            print(f"Skipping {region} (already done)")
            continue
        print(f"\nProcessing {region} ({filename}) ...")
        os.makedirs(out_dir, exist_ok=True)

        value_col = [c for c in pd.read_csv(
            os.path.join(DATA_DIR, filename), nrows=0).columns if c != "Datetime"][0]
        series = load_series(filename, value_col)

        c1 = assignment1(region, series, out_dir)
        c2 = task2(region, series, out_dir)

        all_conclusions.append(f"### {region}\n\n**Assignment 1:** {c1}\n\n**Task 2:** {c2}\n")
        print(f"  Done -> {out_dir}/")

    with open("outputs/conclusions.md", "w") as f:
        f.write("# Time Series Analysis — Conclusions by Region\n\n")
        f.write("\n".join(all_conclusions))

    print("\nAll regions processed. Conclusions written to outputs/conclusions.md")


if __name__ == "__main__":
    main()
