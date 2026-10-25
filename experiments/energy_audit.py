"""Audit of the simulated energy metric.

``total_energy_consumed`` is capped at each node's initial budget because node
energy is clamped at zero.  FCFS/SJF/EDF do not check residual energy, so they
can keep running work on exhausted nodes; the cap then hides part of their
energy demand.  This script reports the uncapped demand and the overdraw next
to the capped metric.

Run after ``experiments/run_experiments.py``.
"""

import os

import pandas as pd

RAW = "results/raw/experiment_results.csv"
OUT = "results/tables/energy_audit.csv"
METRICS = ["total_energy_consumed", "total_energy_demand", "energy_overdraw"]


def main():
    df = pd.read_csv(RAW)
    missing = [m for m in METRICS if m not in df.columns]
    if missing:
        raise SystemExit(f"{RAW} lacks {missing}; re-run experiments/run_experiments.py")

    summary = df.groupby(["workload", "algorithm"])[METRICS].agg(["mean", "std"])
    summary.columns = [f"{m}_{stat}" for m, stat in summary.columns]
    summary = summary.reset_index()
    summary["workload"] = pd.Categorical(
        summary["workload"], ["light", "moderate", "heavy"], ordered=True
    )
    summary = summary.sort_values(["workload", "algorithm"])

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    summary.to_csv(OUT, index=False)
    print(summary[["workload", "algorithm", "total_energy_consumed_mean",
                   "total_energy_demand_mean", "energy_overdraw_mean"]]
          .round(1).to_string(index=False))
    print(f"\nSaved to {OUT}")


if __name__ == "__main__":
    main()
