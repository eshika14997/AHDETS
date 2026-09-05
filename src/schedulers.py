from typing import List, Tuple

from src.models import Task, EdgeNode


def fcfs_schedule(
    tasks: List[Task],
    nodes: List[EdgeNode]
) -> List[Tuple[int, int]]:
    """
    First Come, First Served scheduling.

    Tasks are processed according to their arrival time.
    Each task is assigned to the node that gives the
    earliest possible completion time.

    Returns
    -------
    list of (task_id, node_id)
    """

    # Sort tasks by arrival time.
    ordered_tasks = sorted(
        tasks,
        key=lambda task: task.arrival_time
    )

    # Keep track of when each node becomes available.
    node_available = {
        node.node_id: node.available_time
        for node in nodes
    }

    assignments = []

    for task in ordered_tasks:

        best_node = None
        earliest_finish = float("inf")

        for node in nodes:

            execution_time = node.execution_time(
                task.length
            )

            start_time = max(
                task.arrival_time,
                node_available[node.node_id]
            )

            finish_time = start_time + execution_time

            if finish_time < earliest_finish:
                earliest_finish = finish_time
                best_node = node

        # Assign the task to the selected node.
        assignments.append(
            (task.task_id, best_node.node_id)
        )

        # Update the temporary availability.
        execution_time = best_node.execution_time(
            task.length
        )

        start_time = max(
            task.arrival_time,
            node_available[best_node.node_id]
        )

        node_available[best_node.node_id] = (
            start_time + execution_time
        )

    return assignments


def sjf_schedule(
    tasks: List[Task],
    nodes: List[EdgeNode]
) -> List[Tuple[int, int]]:
    """
    Shortest Job First scheduling.

    Tasks are ordered by their computational length.
    Each task is assigned to the node that gives the
    earliest possible completion time.

    Returns
    -------
    list of (task_id, node_id)
    """

    # Sort tasks from shortest to longest.
    ordered_tasks = sorted(
        tasks,
        key=lambda task: task.length
    )

    # Track temporary node availability.
    node_available = {
        node.node_id: node.available_time
        for node in nodes
    }

    assignments = []

    for task in ordered_tasks:

        best_node = None
        earliest_finish = float("inf")

        for node in nodes:

            execution_time = node.execution_time(
                task.length
            )

            start_time = max(
                task.arrival_time,
                node_available[node.node_id]
            )

            finish_time = start_time + execution_time

            if finish_time < earliest_finish:
                earliest_finish = finish_time
                best_node = node

        assignments.append(
            (task.task_id, best_node.node_id)
        )

        # Update temporary node availability.
        execution_time = best_node.execution_time(
            task.length
        )

        start_time = max(
            task.arrival_time,
            node_available[best_node.node_id]
        )

        node_available[best_node.node_id] = (
            start_time + execution_time
        )

    return assignments

def edf_schedule(
    tasks: List[Task],
    nodes: List[EdgeNode]
) -> List[Tuple[int, int]]:
    ordered_tasks = sorted(tasks, key=lambda task: task.deadline)

    node_available = {
        node.node_id: node.available_time
        for node in nodes
    }

    assignments = []

    for task in ordered_tasks:
        best_node = None
        earliest_finish = float("inf")

        for node in nodes:
            execution_time = node.execution_time(task.length)

            start_time = max(
                task.arrival_time,
                node_available[node.node_id]
            )

            finish_time = start_time + execution_time

            if finish_time < earliest_finish:
                earliest_finish = finish_time
                best_node = node

        assignments.append((task.task_id, best_node.node_id))

        execution_time = best_node.execution_time(task.length)

        start_time = max(
            task.arrival_time,
            node_available[best_node.node_id]
        )

        node_available[best_node.node_id] = start_time + execution_time

    return assignments

def calculate_adaptive_weights(nodes):
    """
    Calculate AHDETS weights based on current system conditions.

    Returns weights for:
    - deadline urgency
    - execution speed
    - spare capacity
    - residual energy
    """

    if not nodes:
        raise ValueError("At least one node is required.")

    # Average residual energy
    average_energy = sum(
        node.energy / node.initial_energy
        if node.initial_energy > 0 else 0.0
        for node in nodes
    ) / len(nodes)

    # Average utilization
    utilizations = [
        node.utilization(node.available_time)
        for node in nodes
    ]

    average_utilization = sum(utilizations) / len(utilizations)

    # Base weights
    deadline_weight = 0.40
    execution_weight = 0.25
    capacity_weight = 0.20
    energy_weight = 0.15

    # Adapt to low-energy condition
    if average_energy < 0.30:
        energy_weight += 0.15
        deadline_weight -= 0.05
        execution_weight -= 0.05
        capacity_weight -= 0.05

    # Adapt to high-utilization condition
    if average_utilization > 0.80:
        capacity_weight += 0.15
        deadline_weight -= 0.05
        execution_weight -= 0.05
        energy_weight -= 0.05

    weights = {
        "deadline": deadline_weight,
        "execution": execution_weight,
        "capacity": capacity_weight,
        "energy": energy_weight
    }

    return weights

def ahdets_schedule(
    tasks: List[Task],
    nodes: List[EdgeNode],
    current_time: float = 0.0,
    weights=None
) -> List[Tuple[int, int]]:

    if weights is None:
        weights = calculate_adaptive_weights(nodes)

    node_available = {
        node.node_id: node.available_time
        for node in nodes
    }

    assignments = []

    # Schedule tasks in arrival order
    ordered_tasks = sorted(tasks, key=lambda task: task.arrival_time)

    for task in ordered_tasks:

        best_node = None
        best_priority = float("-inf")

        for node in nodes:

            # 1. Deadline urgency
            time_to_deadline = max(
                task.deadline - current_time,
                0.001
            )

            deadline_factor = 1.0 / time_to_deadline

            # 2. Execution speed
            execution_time = node.execution_time(task.length)

            execution_factor = 1.0 / max(
                execution_time,
                0.001
            )

            # 3. Spare capacity
            utilization = node.utilization(current_time)

            capacity_factor = 1.0 - utilization

            # 4. Residual energy
            energy_factor = (
                node.energy / node.initial_energy
                if node.initial_energy > 0
                else 0.0
            )

            # AHDETS priority
            priority = (
                weights["deadline"] * deadline_factor
                + weights["execution"] * execution_factor
                + weights["capacity"] * capacity_factor
                + weights["energy"] * energy_factor
            )

            if priority > best_priority:
                best_priority = priority
                best_node = node

        assignments.append(
            (task.task_id, best_node.node_id)
        )

        # Update estimated node availability
        execution_time = best_node.execution_time(task.length)

        start_time = max(
            task.arrival_time,
            node_available[best_node.node_id]
        )

        node_available[best_node.node_id] = (
            start_time + execution_time
        )

    return assignments