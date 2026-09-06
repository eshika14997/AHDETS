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

def ahdets_schedule(tasks, nodes, weights=None):
    """
    AHDETS scheduling with adaptive weights.

    The scheduler maintains a local estimate of node state so that
    weights and priorities can adapt as tasks are assigned.
    """

    import copy

    working_nodes = copy.deepcopy(nodes)

    assignments = []

    # Process tasks in arrival order
    sorted_tasks = sorted(
        tasks,
        key=lambda task: task.arrival_time
    )

    for task in sorted_tasks:

        # Current scheduling time
        current_time = max(
            task.arrival_time,
            min(node.available_time for node in working_nodes)
        )

        # Recalculate adaptive weights using current node state
        adaptive_weights = calculate_adaptive_weights(
            working_nodes
        )

        best_node = None
        best_score = float("-inf")

        for node in working_nodes:

            execution_time = node.execution_time(
                task.length
            )

            # Deadline urgency
            remaining_time = max(
                task.deadline - current_time,
                0.001
            )

            deadline_urgency = 1.0 / remaining_time

            # Faster nodes get higher score
            execution_factor = 1.0 / max(
                execution_time,
                0.001
            )

            # Spare capacity
            utilization = node.utilization(
                max(current_time, 0.001)
            )

            spare_capacity = 1.0 - utilization

            # Residual energy
            residual_energy = (
                node.energy / node.initial_energy
                if node.initial_energy > 0
                else 0.0
            )

            score = (
                adaptive_weights["deadline"] * deadline_urgency
                + adaptive_weights["execution"] * execution_factor
                + adaptive_weights["capacity"] * spare_capacity
                + adaptive_weights["energy"] * residual_energy
            )

            # Prefer the node with the highest score
            if score > best_score:
                best_score = score
                best_node = node

        # Assign task
        execution_time = best_node.execution_time(
            task.length
        )

        start_time = max(
            task.arrival_time,
            best_node.available_time
        )

        finish_time = start_time + execution_time

        assignments.append(
            (task.task_id, best_node.node_id)
        )

        # Update local node state
        best_node.available_time = finish_time
        best_node.busy_time += execution_time
        best_node.total_tasks += 1

        best_node.consume_energy(
            execution_time,
            1.0
        )

    return assignments