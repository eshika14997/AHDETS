
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
CSV = BASE / "results" / "tables" / "load_sensitivity_summary.csv"
OUT = BASE / "results" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(CSV)
df["offered_load_percent"] = df["offered_load"] * 100

metrics = [
    ("deadline_success_rate_mean", "deadline_success_rate_std",
     "Deadline Success Rate vs Offered Load",
     "Deadline Success Rate (%)", "load_sensitivity_deadline_success_rate.png", True),
    ("response_time_mean", "response_time_std",
     "Average Response Time vs Offered Load",
     "Average Response Time", "load_sensitivity_response_time.png", False),
    ("utilization_mean", "utilization_std",
     "System Utilization vs Offered Load",
     "System Utilization (%)", "load_sensitivity_utilization.png", True),
    ("energy_mean", "energy_std",
     "Simulated Energy Consumption vs Offered Load",
     "Simulated Energy Consumption", "load_sensitivity_energy.png", False),
]

for mean_col, std_col, title, ylabel, filename, percent in metrics:
    plt.figure(figsize=(8, 5))
    for algorithm in ["FCFS", "SJF", "EDF", "AHDETS"]:
        d = df[df["algorithm"] == algorithm].sort_values("offered_load_percent")
        y = d[mean_col].to_numpy()
        sd = d[std_col].to_numpy()
        if percent:
            y = y * 100
            sd = sd * 100
        plt.errorbar(
            d["offered_load_percent"], y, yerr=sd,
            marker="o", capsize=3, label=algorithm
        )
    plt.xlabel("Offered Load (%)")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / filename, dpi=300, bbox_inches="tight")
    plt.close()

print("4 figures generated successfully in:")
print(OUT)
