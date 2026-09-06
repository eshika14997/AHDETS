import os
import pandas as pd
from scipy import stats


INPUT_FILE = "results/raw/experiment_results.csv"
OUTPUT_FILE = "results/tables/summary_results.csv"


def calculate_summary(data):
    metric_columns = [
        "deadline_success_rate",
        "average_response_time",
        "system_utilization",
        "total_energy_consumed"
    ]

    rows = []

    grouped = data.groupby(
        ["workload", "algorithm"]
    )

    for (workload, algorithm), group in grouped:

        row = {
            "workload": workload,
            "algorithm": algorithm,
            "runs": len(group)
        }

        for metric in metric_columns:

            values = group[metric]

            mean = values.mean()
            std = values.std(ddof=1)

            confidence_interval = stats.t.interval(
                0.95,
                df=len(values) - 1,
                loc=mean,
                scale=stats.sem(values)
            )

            row[f"{metric}_mean"] = mean
            row[f"{metric}_std"] = std
            row[f"{metric}_ci_lower"] = confidence_interval[0]
            row[f"{metric}_ci_upper"] = confidence_interval[1]

        rows.append(row)

    return pd.DataFrame(rows)


def main():

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(
            f"Could not find {INPUT_FILE}"
        )

    os.makedirs(
        "results/tables",
        exist_ok=True
    )

    data = pd.read_csv(INPUT_FILE)

    summary = calculate_summary(data)

    summary.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Summary saved to: {OUTPUT_FILE}"
    )

    print(
        f"\nAnalyzed {len(data)} experiments."
    )


if __name__ == "__main__":
    main()