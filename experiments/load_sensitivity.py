import copy
import os
import sys
import pandas as pd

# Allow imports from project root
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from src.schedulers import (
    fcfs_schedule,
    sjf_schedule,
    edf_schedule,
    ahdets_schedule
)

from src.task_generator import generate_tasks
from src.simulator import Simulator
from src.metrics import calculate_metrics
from src.utils import create_edge_nodes

from experiments.configuration import (
    NUM_TASKS,
    NUM_RUNS,
    BASE_SEED
)


# ============================================================
# LOAD SENSITIVITY CONFIGURATION
# ============================================================

# Seven workload points.
#
# The original experiments used:
#   Light    = λ 3
#   Moderate = λ 12
#   Heavy    = λ 18
#
# Here we add intermediate points and one higher-load point.

LOAD_POINTS = {
    "3": 3.0,
    "6": 6.0,
    "9": 9.0,
    "12": 12.0,
    "15": 15.0,
    "18": 18.0,
    "21": 21.0,
}


ALGORITHMS = {
    "FCFS": fcfs_schedule,
    "SJF": sjf_schedule,
    "EDF": edf_schedule,
    "AHDETS": ahdets_schedule,
}


# Aggregate capacity of the 10 heterogeneous nodes.
AGGREGATE_CAPACITY = 16250.0

# Mean task length for uniform [50, 2000].
MEAN_TASK_LENGTH = 1025.0


def offered_load(arrival_rate):
    """
    Approximate offered system load.

    rho = lambda * E[L] / aggregate capacity
    """

    return (
        arrival_rate
        * MEAN_TASK_LENGTH
        / AGGREGATE_CAPACITY
    )


def run_one(algorithm, arrival_rate, seed):
    """
    Run one scheduler for one arrival rate and seed.
    """

    # Generate the same task workload for all schedulers
    # for this seed.
    tasks = generate_tasks(
        NUM_TASKS,
        arrival_rate,
        seed=seed
    )

    # Independent node state for scheduler.
    scheduler_nodes = create_edge_nodes()

    assignments = algorithm(
        tasks,
        copy.deepcopy(scheduler_nodes)
    )

    # Fresh node state for actual simulation.
    simulation_nodes = create_edge_nodes()

    simulator = Simulator(
        simulation_nodes
    )

    completed_tasks, final_nodes = simulator.run(
        tasks,
        assignments
    )

    return calculate_metrics(
        completed_tasks,
        final_nodes
    )


def main():

    rows = []

    total = (
        len(LOAD_POINTS)
        * len(ALGORITHMS)
        * NUM_RUNS
    )

    done = 0

    print("=" * 70)
    print("AHDETS LOAD SENSITIVITY EXPERIMENT")
    print("=" * 70)

    print(
        f"Tasks per run : {NUM_TASKS}"
    )

    print(
        f"Runs per point: {NUM_RUNS}"
    )

    print(
        f"Load points  : {len(LOAD_POINTS)}"
    )

    print()

    # ========================================================
    # RUN EXPERIMENT
    # ========================================================

    for load_label, arrival_rate in LOAD_POINTS.items():

        load = offered_load(
            arrival_rate
        )

        print(
            f"\nArrival rate λ={arrival_rate:.1f} "
            f"| offered load ≈ {load * 100:.1f}%"
        )

        for name, algorithm in ALGORITHMS.items():

            for run in range(NUM_RUNS):

                seed = BASE_SEED + run

                metrics = run_one(
                    algorithm,
                    arrival_rate,
                    seed
                )

                rows.append({
                    "arrival_rate":
                        arrival_rate,

                    "offered_load":
                        load,

                    "offered_load_percent":
                        load * 100,

                    "algorithm":
                        name,

                    "run":
                        run + 1,

                    **metrics
                })

                done += 1

            print(
                f"  {name}: "
                f"{NUM_RUNS} runs completed"
            )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    raw_dir = "results/raw"
    table_dir = "results/tables"

    os.makedirs(
        raw_dir,
        exist_ok=True
    )

    os.makedirs(
        table_dir,
        exist_ok=True
    )

    raw = pd.DataFrame(rows)

    raw_path = os.path.join(
        raw_dir,
        "load_sensitivity_results.csv"
    )

    raw.to_csv(
        raw_path,
        index=False
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    summary = (
        raw
        .groupby(
            [
                "arrival_rate",
                "offered_load",
                "algorithm"
            ]
        )
        .agg(
            deadline_success_rate_mean=(
                "deadline_success_rate",
                "mean"
            ),

            deadline_success_rate_std=(
                "deadline_success_rate",
                "std"
            ),

            response_time_mean=(
                "average_response_time",
                "mean"
            ),

            response_time_std=(
                "average_response_time",
                "std"
            ),

            utilization_mean=(
                "system_utilization",
                "mean"
            ),

            utilization_std=(
                "system_utilization",
                "std"
            ),

            energy_mean=(
                "total_energy_consumed",
                "mean"
            ),

            energy_std=(
                "total_energy_consumed",
                "std"
            ),
        )
        .reset_index()
    )

    summary_path = os.path.join(
        table_dir,
        "load_sensitivity_summary.csv"
    )

    summary.to_csv(
        summary_path,
        index=False
    )

    # ========================================================
    # FINISHED
    # ========================================================

    print()
    print("=" * 70)
    print("LOAD SENSITIVITY EXPERIMENT COMPLETE")
    print("=" * 70)

    print(
        f"Total experiments: {done}/{total}"
    )

    print(
        f"\nRaw results saved to:"
    )

    print(
        raw_path
    )

    print(
        f"\nSummary saved to:"
    )

    print(
        summary_path
    )


if __name__ == "__main__":
    main()