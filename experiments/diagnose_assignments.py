import copy
import os
import sys
from collections import Counter

# Add project root to Python path
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from src.task_generator import generate_tasks
from src.schedulers import (
    fcfs_schedule,
    sjf_schedule,
    edf_schedule,
    ahdets_schedule
)
from src.utils import create_edge_nodes


def diagnose():

    tasks = generate_tasks(
        num_tasks=100,
        arrival_rate=15.0,
        seed=42
    )

    algorithms = {
        "FCFS": fcfs_schedule,
        "SJF": sjf_schedule,
        "EDF": edf_schedule,
        "AHDETS": ahdets_schedule
    }

    for name, algorithm in algorithms.items():

        nodes = create_edge_nodes()

        assignments = algorithm(
            copy.deepcopy(tasks),
            nodes
        )

        counts = Counter(
            node_id
            for _, node_id in assignments
        )

        print(f"\n{name}")
        print("-" * 30)

        for node in nodes:
            print(
                f"Node {node.node_id} "
                f"({node.capacity} MIPS): "
                f"{counts.get(node.node_id, 0)} tasks"
            )


if __name__ == "__main__":
    diagnose()