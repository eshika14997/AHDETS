import copy
import csv
from pathlib import Path

from src.task_generator import generate_tasks
from src.utils import create_edge_nodes
from src.simulator import Simulator
from src.metrics import calculate_metrics
from src.schedulers import ahdets_schedule
from experiments.configuration import NUM_TASKS, WORKLOADS, NUM_RUNS, BASE_SEED


ABLATION_VARIANTS = {
    "AHDETS": None,
    "No_Deadline": {"deadline"},
    "No_Execution": {"execution"},
    "No_Capacity": {"capacity"},
    "No_Energy": {"energy"},
}


def run_single_ablation(variant, arrival_rate, seed):
    tasks = generate_tasks(
        num_tasks=NUM_TASKS,
        arrival_rate=arrival_rate,
        seed=seed
    )

    nodes = create_edge_nodes()
    scheduler_nodes = copy.deepcopy(nodes)

    enabled_factors = None

    if ABLATION_VARIANTS[variant] is not None:
        all_factors = {"deadline", "execution", "capacity", "energy"}
        enabled_factors = all_factors - ABLATION_VARIANTS[variant]

    assignments = ahdets_schedule(
        tasks,
        scheduler_nodes,
        enabled_factors=enabled_factors
    )

    simulation_nodes = create_edge_nodes()
    simulator = Simulator(simulation_nodes)

    completed_tasks, final_nodes = simulator.run(
        tasks,
        assignments
    )

    return calculate_metrics(
        completed_tasks,
        final_nodes
    )


def main():
    output_path = Path("results/raw/ablation_results.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []

    total_runs = len(ABLATION_VARIANTS) * len(WORKLOADS) * NUM_RUNS
    completed = 0

    for workload, arrival_rate in WORKLOADS.items():

        for variant in ABLATION_VARIANTS:

            for run in range(NUM_RUNS):

                seed = BASE_SEED + run

                metrics = run_single_ablation(
                    variant,
                    arrival_rate,
                    seed
                )

                rows.append({
                    "workload": workload,
                    "variant": variant,
                    "run": run + 1,
                    "deadline_success_rate": metrics["deadline_success_rate"],
                    "average_response_time": metrics["average_response_time"],
                    "system_utilization": metrics["system_utilization"],
                    "total_energy_consumed": metrics["total_energy_consumed"],
                })

                completed += 1

                if completed % 30 == 0:
                    print(
                        f"Completed {completed}/{total_runs} runs"
                    )

    fieldnames = [
        "workload",
        "variant",
        "run",
        "deadline_success_rate",
        "average_response_time",
        "system_utilization",
        "total_energy_consumed",
    ]

    with output_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Ablation experiments completed: {total_runs}")
    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()