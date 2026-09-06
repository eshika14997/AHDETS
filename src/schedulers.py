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
    Calculate adaptive AHDETS weights based on
    current average system energy and utilization.

    Base weights:
    - Deadline urgency: 0.40
    - Execution efficiency: 0.25
    - Spare capacity: 0.20
    - Residual energy: 0.15

    The weights are adjusted continuously:
    - Higher utilization increases the importance of capacity.
    - Lower residual energy increases the importance of energy.
    """

    if not nodes:
        raise ValueError("At least one node is required.")

    # Average residual energy
    energy_levels = [
        node.energy / node.initial_energy
        if node.initial_energy > 0 else 0.0
        for node in nodes
    ]

    average_energy = sum(energy_levels) / len(energy_levels)

    # Average utilization
    utilizations = [
        node.utilization(node.available_time)
        for node in nodes
    ]

    average_utilization = sum(utilizations) / len(utilizations)

    # ---------------------------------------------------------
    # Base weights
    # ---------------------------------------------------------

    deadline_weight = 0.40
    execution_weight = 0.25
    capacity_weight = 0.20
    energy_weight = 0.15

    # ---------------------------------------------------------
    # Adaptive adjustment
    # ---------------------------------------------------------

    # As utilization increases, give more importance
    # to spare capacity.
    capacity_adjustment = 0.15 * average_utilization

    # As energy decreases, give more importance
    # to residual energy.
    energy_adjustment = 0.15 * (1.0 - average_energy)

    capacity_weight += capacity_adjustment
    energy_weight += energy_adjustment

    # Take the additional weight proportionally
    # from deadline and execution factors.
    total_adjustment = (
        capacity_adjustment +
        energy_adjustment
    )

    deadline_reduction = (
        total_adjustment * 0.60
    )

    execution_reduction = (
        total_adjustment * 0.40
    )

    deadline_weight -= deadline_reduction
    execution_weight -= execution_reduction

    # ---------------------------------------------------------
    # Safety: prevent negative weights
    # ---------------------------------------------------------

    weights = {
        "deadline": max(deadline_weight, 0.0),
        "execution": max(execution_weight, 0.0),
        "capacity": max(capacity_weight, 0.0),
        "energy": max(energy_weight, 0.0)
    }

    # Normalize so weights sum exactly to 1
    total = sum(weights.values())

    for key in weights:
        weights[key] /= total

    return weights

def ahdets_schedule(tasks, nodes, weights=None):
    """
    AHDETS scheduling with adaptive weights.

    Considers:
    1. Deadline urgency
    2. Execution efficiency
    3. Spare capacity
    4. Residual energy
    """

    import copy

    working_nodes = copy.deepcopy(nodes)
    assignments = []

    sorted_tasks = sorted(
        tasks,
        key=lambda task: task.arrival_time
    )

    for task in sorted_tasks:

        if weights is None:
            adaptive_weights = calculate_adaptive_weights(
                working_nodes
            )
        else:
            adaptive_weights = weights

        candidates = []

        for node in working_nodes:

            # Time required by this node
            execution_time = node.execution_time(
                task.length
            )

            # When this node can start the task
            start_time = max(
                task.arrival_time,
                node.available_time
            )

            # Predicted completion time
            predicted_finish = (
                start_time + execution_time
            )

            # -------------------------------------------------
            # 1. Deadline factor
            # -------------------------------------------------

            deadline_slack = (
                task.deadline - predicted_finish
            )

            if deadline_slack >= 0:
                deadline_factor = (
                    1.0 /
                    (1.0 + deadline_slack)
                )
            else:
                deadline_factor = (
                    1.0 /
                    (1.0 + abs(deadline_slack))
                )

            # -------------------------------------------------
            # 2. Execution efficiency
            # -------------------------------------------------

            execution_factor = (
                1.0 /
                max(execution_time, 0.001)
            )

            # -------------------------------------------------
            # 3. Spare capacity
            # -------------------------------------------------

            utilization = node.utilization(
                max(start_time, 0.001)
            )

            spare_capacity = 1.0 - utilization

            # -------------------------------------------------
            # 4. Residual energy
            # -------------------------------------------------

            if node.initial_energy > 0:
                residual_energy = (
                    node.energy /
                    node.initial_energy
                )
            else:
                residual_energy = 0.0

            candidates.append({
                "node": node,
                "deadline": deadline_factor,
                "execution": execution_factor,
                "capacity": spare_capacity,
                "energy": residual_energy
            })

        # -----------------------------------------------------
        # Normalize factors across candidate nodes
        # -----------------------------------------------------

        for factor in [
            "deadline",
            "execution",
            "capacity",
            "energy"
        ]:

            values = [
                candidate[factor]
                for candidate in candidates
            ]

            min_value = min(values)
            max_value = max(values)

            if max_value == min_value:

                for candidate in candidates:
                    candidate[
                        f"{factor}_normalized"
                    ] = 1.0

            else:

                for candidate in candidates:
                    candidate[
                        f"{factor}_normalized"
                    ] = (
                        candidate[factor] - min_value
                    ) / (
                        max_value - min_value
                    )

        # -----------------------------------------------------
        # Calculate weighted AHDETS score
        # -----------------------------------------------------

        best_node = None
        best_score = float("-inf")

        for candidate in candidates:

            score = (
                adaptive_weights["deadline"]
                * candidate["deadline_normalized"]

                + adaptive_weights["execution"]
                * candidate["execution_normalized"]

                + adaptive_weights["capacity"]
                * candidate["capacity_normalized"]

                + adaptive_weights["energy"]
                * candidate["energy_normalized"]
            )

            if score > best_score:
                best_score = score
                best_node = candidate["node"]

        # -----------------------------------------------------
        # Assign task
        # -----------------------------------------------------

        execution_time = best_node.execution_time(
            task.length
        )

        start_time = max(
            task.arrival_time,
            best_node.available_time
        )

        finish_time = (
            start_time + execution_time
        )

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