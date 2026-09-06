import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon


INPUT_FILE = Path("results/raw/ablation_results.csv")

SUMMARY_FILE = Path("results/tables/ablation_summary.csv")
STATISTICS_FILE = Path("results/tables/ablation_statistical_tests.csv")

PLOTS_DIR = Path("results/plots")

METRICS = [
    "deadline_success_rate",
    "average_response_time",
    "system_utilization",
    "total_energy_consumed",
]

VARIANTS = [
    "AHDETS",
    "No_Deadline",
    "No_Execution",
    "No_Capacity",
    "No_Energy",
]

ABLATIONS = [
    "No_Deadline",
    "No_Execution",
    "No_Capacity",
    "No_Energy",
]

WORKLOADS = [
    "light",
    "moderate",
    "heavy",
]


def confidence_interval(values):
    """Return mean, standard deviation and 95% CI."""
    values = np.asarray(values, dtype=float)

    mean = np.mean(values)
    std = np.std(values, ddof=1)

    n = len(values)

    if n > 1:
        margin = 1.96 * std / math.sqrt(n)
        ci_lower = mean - margin
        ci_upper = mean + margin
    else:
        ci_lower = mean
        ci_upper = mean

    return mean, std, ci_lower, ci_upper


def holm_bonferroni(p_values):
    """Apply Holm-Bonferroni correction."""
    p_values = np.asarray(p_values, dtype=float)

    order = np.argsort(p_values)
    adjusted = np.empty(len(p_values), dtype=float)

    previous = 0.0

    for rank, index in enumerate(order):
        adjusted_value = (len(p_values) - rank) * p_values[index]
        adjusted_value = max(adjusted_value, previous)
        adjusted_value = min(adjusted_value, 1.0)

        adjusted[index] = adjusted_value
        previous = adjusted_value

    return adjusted


def create_summary(df):
    rows = []

    for workload in WORKLOADS:
        for variant in VARIANTS:

            subset = df[
                (df["workload"] == workload)
                & (df["variant"] == variant)
            ]

            for metric in METRICS:
                mean, std, ci_lower, ci_upper = confidence_interval(
                    subset[metric]
                )

                rows.append({
                    "workload": workload,
                    "variant": variant,
                    "metric": metric,
                    "runs": len(subset),
                    "mean": mean,
                    "std": std,
                    "ci_lower": ci_lower,
                    "ci_upper": ci_upper,
                })

    return pd.DataFrame(rows)


def create_statistical_tests(df):
    rows = []

    for workload in WORKLOADS:

        full = df[
            (df["workload"] == workload)
            & (df["variant"] == "AHDETS")
        ].sort_values("run")

        for ablation in ABLATIONS:

            ablated = df[
                (df["workload"] == workload)
                & (df["variant"] == ablation)
            ].sort_values("run")

            for metric in METRICS:

                full_values = full[metric].to_numpy(dtype=float)
                ablated_values = ablated[metric].to_numpy(dtype=float)

                differences = full_values - ablated_values

                # Wilcoxon signed-rank test
                try:
                    statistic, p_value = wilcoxon(
                        full_values,
                        ablated_values,
                        zero_method="wilcox",
                        alternative="two-sided",
                    )
                except ValueError:
                    statistic = np.nan
                    p_value = 1.0

                mean_difference = np.mean(differences)

                # Cohen's dz
                difference_std = np.std(
                    differences,
                    ddof=1
                )

                if difference_std > 0:
                    cohens_dz = mean_difference / difference_std
                else:
                    cohens_dz = 0.0

                rows.append({
                    "workload": workload,
                    "comparison": f"AHDETS_vs_{ablation}",
                    "ablation": ablation,
                    "metric": metric,
                    "mean_AHDETS": np.mean(full_values),
                    "mean_ablation": np.mean(ablated_values),
                    "mean_difference": mean_difference,
                    "wilcoxon_statistic": statistic,
                    "wilcoxon_p": p_value,
                    "cohens_dz": cohens_dz,
                })

    results = pd.DataFrame(rows)

    # Holm-Bonferroni correction across all 48 comparisons
    results["holm_adjusted_p"] = holm_bonferroni(
        results["wilcoxon_p"].to_numpy()
    )

    results["significant"] = (
        results["holm_adjusted_p"] < 0.05
    )

    return results


def create_plots(df):
    import matplotlib.pyplot as plt

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    metric_titles = {
        "deadline_success_rate":
            "Deadline Success Rate",
        "average_response_time":
            "Average Response Time",
        "system_utilization":
            "System Utilization",
        "total_energy_consumed":
            "Total Energy Consumed",
    }

    for metric in METRICS:

        plt.figure(figsize=(10, 6))

        for variant in VARIANTS:
            means = []

            for workload in WORKLOADS:
                subset = df[
                    (df["workload"] == workload)
                    & (df["variant"] == variant)
                ]

                means.append(
                    subset[metric].mean()
                )

            plt.plot(
                WORKLOADS,
                means,
                marker="o",
                label=variant
            )

        plt.xlabel("Workload")
        plt.ylabel(metric_titles[metric])
        plt.title(
            f"AHDETS Ablation Study: "
            f"{metric_titles[metric]}"
        )
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = PLOTS_DIR / f"ablation_{metric}.png"
        plt.savefig(filename, dpi=300)
        plt.close()

        print(f"Created plot: {filename}")


def main():

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    expected_rows = (
        len(WORKLOADS)
        * len(VARIANTS)
        * 30
    )

    if len(df) != expected_rows:
        raise ValueError(
            f"Expected {expected_rows} rows, "
            f"but found {len(df)}."
        )

    print(f"Loaded {len(df)} ablation runs.")

    # --------------------------------------------------
    # Summary statistics
    # --------------------------------------------------

    summary = create_summary(df)

    SUMMARY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    summary.to_csv(
        SUMMARY_FILE,
        index=False
    )

    print(f"Saved summary: {SUMMARY_FILE}")

    # --------------------------------------------------
    # Statistical tests
    # --------------------------------------------------

    statistics = create_statistical_tests(df)

    statistics.to_csv(
        STATISTICS_FILE,
        index=False
    )

    print(
        f"Saved statistical tests: "
        f"{STATISTICS_FILE}"
    )

    significant_count = (
        statistics["significant"].sum()
    )

    total_tests = len(statistics)

    print()
    print(
        f"Significant after Holm-Bonferroni: "
        f"{significant_count}/{total_tests}"
    )

    print(
        f"Non-significant: "
        f"{total_tests - significant_count}/{total_tests}"
    )

    # --------------------------------------------------
    # Plots
    # --------------------------------------------------

    create_plots(df)

    print()
    print("Ablation analysis completed successfully.")


if __name__ == "__main__":
    main()