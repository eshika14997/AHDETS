"""
Statistical significance testing for AHDETS experiments.

This script compares AHDETS against FCFS, SJF, and EDF using
paired statistical tests because the same workload seed is used
for all algorithms within each run.

Tests:
    - Wilcoxon signed-rank test
    - Paired t-test
    - Cohen's dz effect size
    - Holm-Bonferroni multiple-comparison correction

Metrics:
    - Deadline success rate
    - Average response time
    - System utilization
    - Total energy consumed

Output:
    results/tables/statistical_tests.csv
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ttest_rel, wilcoxon


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "results" / "raw" / "experiment_results.csv"
OUTPUT_FILE = PROJECT_ROOT / "results" / "tables" / "statistical_tests.csv"

ALGORITHMS = ["FCFS", "SJF", "EDF"]

METRICS = [
    "deadline_success_rate",
    "average_response_time",
    "system_utilization",
    "total_energy_consumed",
]

ALPHA = 0.05


# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def cohens_dz(x, y):
    """
    Calculate Cohen's dz for paired samples.

    dz = mean(x - y) / std(x - y)

    Returns NaN when the paired differences have zero variance.
    """
    differences = np.asarray(x) - np.asarray(y)

    std_difference = np.std(differences, ddof=1)

    if std_difference == 0:
        return np.nan

    return np.mean(differences) / std_difference


def interpret_effect_size(dz):
    """
    Interpret the absolute magnitude of Cohen's dz.

    Conventional interpretation:
        < 0.2  -> negligible
        < 0.5  -> small
        < 0.8  -> medium
        >= 0.8 -> large
    """
    if pd.isna(dz):
        return "Not defined"

    magnitude = abs(dz)

    if magnitude < 0.2:
        return "Negligible"
    elif magnitude < 0.5:
        return "Small"
    elif magnitude < 0.8:
        return "Medium"
    else:
        return "Large"


def paired_wilcoxon(x, y):
    """
    Run the Wilcoxon signed-rank test.

    If all paired differences are zero, return p = 1.0.
    """
    differences = np.asarray(x) - np.asarray(y)

    if np.allclose(differences, 0):
        return 1.0

    try:
        result = wilcoxon(
            x,
            y,
            alternative="two-sided",
            zero_method="wilcox",
        )
        return float(result.pvalue)
    except ValueError:
        return np.nan


def paired_ttest(x, y):
    """
    Run a paired t-test.
    """
    result = ttest_rel(x, y)

    if np.isnan(result.pvalue):
        return np.nan

    return float(result.pvalue)


def holm_bonferroni(p_values, alpha=0.05):
    """
    Apply the Holm-Bonferroni correction to a collection of p-values.

    Returns:
        adjusted_p_values
        significant_flags

    NaN p-values are preserved as NaN.
    """
    p_values = np.asarray(p_values, dtype=float)

    adjusted = np.full_like(p_values, np.nan)

    valid_indices = np.where(~np.isnan(p_values))[0]

    if len(valid_indices) == 0:
        return adjusted, np.array([False] * len(p_values))

    valid_p_values = p_values[valid_indices]

    # Sort p-values from smallest to largest.
    order = np.argsort(valid_p_values)
    sorted_p_values = valid_p_values[order]

    m = len(sorted_p_values)

    adjusted_sorted = np.empty(m)

    # Holm adjustment:
    # adjusted p_i = max(previous adjusted p,
    #                     (m-i) * p_i)
    previous = 0.0

    for i, p_value in enumerate(sorted_p_values):
        adjusted_value = (m - i) * p_value
        adjusted_value = max(adjusted_value, previous)
        adjusted_value = min(adjusted_value, 1.0)

        adjusted_sorted[i] = adjusted_value
        previous = adjusted_value

    # Put adjusted values back into their original positions.
    adjusted_valid = np.empty(m)

    for sorted_position, original_position in enumerate(order):
        adjusted_valid[original_position] = adjusted_sorted[
            sorted_position
        ]

    adjusted[valid_indices] = adjusted_valid

    significant = np.zeros(len(p_values), dtype=bool)
    significant[valid_indices] = adjusted_valid < alpha

    return adjusted, significant


# ---------------------------------------------------------------------
# Main statistical analysis
# ---------------------------------------------------------------------

def run_statistical_tests():
    """Run all paired statistical tests and save the results."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_FILE}"
        )

    # Load experimental results.
    df = pd.read_csv(INPUT_FILE)

    required_columns = {
        "workload",
        "algorithm",
        "run",
        *METRICS,
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            "The input CSV is missing the following columns:\n"
            + "\n".join(sorted(missing_columns))
        )

    results = []

    workloads = sorted(df["workload"].unique())

    # -------------------------------------------------------------
    # Generate all 36 comparisons.
    # -------------------------------------------------------------

    for workload in workloads:

        workload_df = df[df["workload"] == workload]

        ahdets_df = workload_df[
            workload_df["algorithm"] == "AHDETS"
        ].sort_values("run")

        for baseline in ALGORITHMS:

            baseline_df = workload_df[
                workload_df["algorithm"] == baseline
            ].sort_values("run")

            # Pair observations using the run number.
            merged = pd.merge(
                ahdets_df[["run"] + METRICS],
                baseline_df[["run"] + METRICS],
                on="run",
                suffixes=("_ahdets", "_baseline"),
            )

            if len(merged) == 0:
                raise ValueError(
                    f"No paired observations found for "
                    f"{workload}: AHDETS vs {baseline}"
                )

            for metric in METRICS:

                ahdets_values = merged[
                    f"{metric}_ahdets"
                ].to_numpy()

                baseline_values = merged[
                    f"{metric}_baseline"
                ].to_numpy()

                # Descriptive statistics.
                ahdets_mean = np.mean(ahdets_values)
                baseline_mean = np.mean(baseline_values)

                mean_difference = (
                    ahdets_mean - baseline_mean
                )

                # Statistical tests.
                wilcoxon_p = paired_wilcoxon(
                    ahdets_values,
                    baseline_values,
                )

                ttest_p = paired_ttest(
                    ahdets_values,
                    baseline_values,
                )

                # Effect size.
                dz = cohens_dz(
                    ahdets_values,
                    baseline_values,
                )

                results.append(
                    {
                        "workload": workload,
                        "comparison": f"AHDETS vs {baseline}",
                        "baseline": baseline,
                        "metric": metric,
                        "runs": len(merged),

                        "ahdets_mean": ahdets_mean,
                        "baseline_mean": baseline_mean,
                        "mean_difference": mean_difference,

                        "wilcoxon_p_value": wilcoxon_p,
                        "paired_ttest_p_value": ttest_p,

                        "cohens_dz": dz,
                        "effect_size": interpret_effect_size(dz),
                    }
                )

    results_df = pd.DataFrame(results)

    # -------------------------------------------------------------
    # Holm-Bonferroni correction
    #
    # Correction is applied across all 36 hypothesis tests.
    # -------------------------------------------------------------

    adjusted_p_values, significant_flags = holm_bonferroni(
        results_df["wilcoxon_p_value"].to_numpy(),
        alpha=ALPHA,
    )

    results_df["holm_adjusted_p_value"] = adjusted_p_values

    results_df["significant_after_holm"] = np.where(
        significant_flags,
        "Yes",
        "No",
    )

    # -------------------------------------------------------------
    # Significance notation based on adjusted p-values.
    # -------------------------------------------------------------

    def significance_marker(p_value):
        if pd.isna(p_value):
            return "NA"

        if p_value < 0.001:
            return "***"
        elif p_value < 0.01:
            return "**"
        elif p_value < 0.05:
            return "*"
        else:
            return "ns"

    results_df["holm_significance"] = (
        results_df["holm_adjusted_p_value"]
        .apply(significance_marker)
    )

    results_df["alpha"] = ALPHA

    # -------------------------------------------------------------
    # Reorder columns for easier reading.
    # -------------------------------------------------------------

    results_df = results_df[
        [
            "workload",
            "comparison",
            "baseline",
            "metric",
            "runs",

            "ahdets_mean",
            "baseline_mean",
            "mean_difference",

            "wilcoxon_p_value",
            "holm_adjusted_p_value",
            "paired_ttest_p_value",

            "cohens_dz",
            "effect_size",

            "alpha",
            "significant_after_holm",
            "holm_significance",
        ]
    ]

    # -------------------------------------------------------------
    # Save results.
    # -------------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    results_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    # -------------------------------------------------------------
    # Print results.
    # -------------------------------------------------------------

    print("\n" + "=" * 100)
    print("AHDETS STATISTICAL SIGNIFICANCE ANALYSIS")
    print("=" * 100)

    print(f"\nInput file:")
    print(INPUT_FILE)

    print(f"\nOutput file:")
    print(OUTPUT_FILE)

    print(
        f"\nTotal statistical comparisons: "
        f"{len(results_df)}"
    )

    print("\nWilcoxon + Holm-Bonferroni results:")
    print("-" * 100)

    for _, row in results_df.iterrows():

        adjusted_p = row["holm_adjusted_p_value"]

        if pd.isna(adjusted_p):
            p_text = "NA"
        else:
            p_text = f"{adjusted_p:.6f}"

        print(
            f"{row['workload']:>8} | "
            f"{row['comparison']:<18} | "
            f"{row['metric']:<25} | "
            f"adjusted p = {p_text:<10} | "
            f"{row['significant_after_holm']:<3} | "
            f"{row['effect_size']}"
        )

    # -------------------------------------------------------------
    # Summary.
    # -------------------------------------------------------------

    significant_count = (
        results_df["significant_after_holm"] == "Yes"
    ).sum()

    total_count = len(results_df)

    print("\n" + "=" * 100)

    print(
        f"Significant after Holm-Bonferroni: "
        f"{significant_count}/{total_count}"
    )

    print(
        f"Non-significant after Holm-Bonferroni: "
        f"{total_count - significant_count}/{total_count}"
    )

    print("=" * 100)

    print(
        "\nSignificance notation uses Holm-adjusted p-values:"
        "\n  ***  p < 0.001"
        "\n  **   p < 0.01"
        "\n  *    p < 0.05"
        "\n  ns   p >= 0.05"
    )

    print(
        "\nStatistical analysis completed successfully."
    )


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------

if __name__ == "__main__":
    run_statistical_tests()