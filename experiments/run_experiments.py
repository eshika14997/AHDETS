import copy
import sys
import os

# Allow imports from the project root
sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from src.models import EdgeNode
from src.task_generator import generate_tasks
from src.schedulers import (
    fcfs_schedule,
    sjf_schedule,
    edf_schedule,
    ahdets_schedule
)
from src.simulator import Simulator
from src.metrics import calculate_metrics
from src.utils import create_edge_nodes

from experiments.configuration import (
    NUM_TASKS,
    WORKLOADS,
    NUM_RUNS,
    BASE_SEED
)


def run_single_experiment(
    algorithm,
    arrival_rate,
    seed
):
    """
    Run one simulation for one scheduling algorithm.
    """

    tasks = generate_tasks(
        num_tasks=NUM_TASKS,
        arrival_rate=arrival_rate,
        seed=seed
    )

    nodes = create_edge_nodes()

    # Scheduler gets independent node state
    scheduler_nodes = copy.deepcopy(nodes)

    assignments = algorithm(
        tasks,
        scheduler_nodes
    )

    # Fresh nodes for actual simulation
    simulation_nodes = create_edge_nodes()

    simulator = Simulator(simulation_nodes)

    completed_tasks, final_nodes = simulator.run(
        tasks,
        assignments
    )

    metrics = calculate_metrics(
        completed_tasks,
        final_nodes
    )

    return metrics


def run_all_experiments():
    """
    Run all algorithms across all workloads and repetitions.
    """

    algorithms = {
        "FCFS": fcfs_schedule,
        "SJF": sjf_schedule,
        "EDF": edf_schedule,
        "AHDETS": ahdets_schedule
    }

    results = []

    for workload_name, arrival_rate in WORKLOADS.items():

        print(
            f"\nRunning workload: {workload_name}"
        )

        for algorithm_name, algorithm in algorithms.items():

            print(
                f"  Algorithm: {algorithm_name}"
            )

            for run in range(NUM_RUNS):

                seed = (
                    BASE_SEED
                    + run
                )

                metrics = run_single_experiment(
                    algorithm,
                    arrival_rate,
                    seed
                )

                result = {
                    "workload": workload_name,
                    "algorithm": algorithm_name,
                    "run": run + 1,
                    **metrics
                }

                results.append(result)

    return results


import pandas as pd


def save_results(results):
    """Save experiment results to a CSV file."""

    os.makedirs("results/raw", exist_ok=True)

    output_file = "results/raw/experiment_results.csv"

    dataframe = pd.DataFrame(results)

    dataframe.to_csv(
        output_file,
        index=False
    )

    print(
        f"\nResults saved to: {output_file}"
    )


if __name__ == "__main__":

    results = run_all_experiments()

    save_results(results)

    print(
        f"Completed {len(results)} experiments."
    )