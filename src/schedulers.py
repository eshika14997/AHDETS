"""Online scheduling policies for the AHDETS simulation.

All schedulers make decisions only from tasks that have arrived by the
current simulation time.  The returned assignment list is in dispatch
order and can therefore be replayed by :class:`src.simulator.Simulator`.
"""

from copy import deepcopy
from typing import Iterable, List, Optional, Set, Tuple

from src.models import EdgeNode, Task

VALID_FACTORS = {"deadline", "execution", "capacity", "energy"}
BASE_WEIGHTS = {
    "deadline": 0.40,
    "execution": 0.25,
    "capacity": 0.20,
    "energy": 0.15,
}
ENERGY_THRESHOLD = 0.30
UTILIZATION_THRESHOLD = 0.80
ADAPTATION_STEP = 0.15


def _reset_working_nodes(nodes: List[EdgeNode]) -> List[EdgeNode]:
    working = deepcopy(nodes)
    for node in working:
        node.available_time = 0.0
        node.busy_time = 0.0
        node.total_tasks = 0
        node.energy = node.initial_energy
    return working


def _task_key(policy: str, task: Task):
    if policy == "fcfs":
        return (task.arrival_time, task.task_id)
    if policy == "sjf":
        return (task.length, task.arrival_time, task.task_id)
    if policy == "edf":
        return (task.deadline, task.arrival_time, task.task_id)
    raise ValueError(f"Unknown policy: {policy}")


def _reserve(task: Task, node: EdgeNode, current_time: float, energy_rate: float):
    execution_time = node.execution_time(task.length)
    start_time = max(current_time, task.arrival_time, node.available_time)
    finish_time = start_time + execution_time

    node.available_time = finish_time
    node.busy_time += execution_time
    node.total_tasks += 1
    node.consume_energy(execution_time, energy_rate)
    return finish_time


def _online_baseline_schedule(
    tasks: List[Task],
    nodes: List[EdgeNode],
    policy: str,
    energy_rate: float = 1.0,
) -> List[Tuple[int, int]]:
    """Work-conserving online FCFS/SJF/EDF dispatcher."""
    if not nodes:
        raise ValueError("At least one node is required.")

    working = _reset_working_nodes(nodes)
    pending: List[Task] = []
    ordered_arrivals = sorted(tasks, key=lambda t: (t.arrival_time, t.task_id))
    next_arrival = 0
    current_time = 0.0
    assignments: List[Tuple[int, int]] = []

    while next_arrival < len(ordered_arrivals) or pending:
        if not pending and next_arrival < len(ordered_arrivals):
            current_time = max(current_time, ordered_arrivals[next_arrival].arrival_time)

        while next_arrival < len(ordered_arrivals) and ordered_arrivals[next_arrival].arrival_time <= current_time + 1e-12:
            pending.append(ordered_arrivals[next_arrival])
            next_arrival += 1

        idle_nodes = [node for node in working if node.available_time <= current_time + 1e-12]

        if not idle_nodes:
            next_free = min(node.available_time for node in working)
            next_arrival_time = (
                ordered_arrivals[next_arrival].arrival_time
                if next_arrival < len(ordered_arrivals)
                else float("inf")
            )
            current_time = min(next_free, next_arrival_time)
            continue

        if not pending:
            continue

        task = min(pending, key=lambda t: _task_key(policy, t))
        pending.remove(task)

        best_node = min(
            idle_nodes,
            key=lambda node: (
                current_time + node.execution_time(task.length),
                node.node_id,
            ),
        )
        assignments.append((task.task_id, best_node.node_id))
        _reserve(task, best_node, current_time, energy_rate)

    return assignments


def fcfs_schedule(tasks: List[Task], nodes: List[EdgeNode]) -> List[Tuple[int, int]]:
    return _online_baseline_schedule(tasks, nodes, "fcfs")


def sjf_schedule(tasks: List[Task], nodes: List[EdgeNode]) -> List[Tuple[int, int]]:
    return _online_baseline_schedule(tasks, nodes, "sjf")


def edf_schedule(tasks: List[Task], nodes: List[EdgeNode]) -> List[Tuple[int, int]]:
    return _online_baseline_schedule(tasks, nodes, "edf")


def calculate_adaptive_weights(nodes: List[EdgeNode], current_time: Optional[float] = None):
    """Adapt AHDETS weights using the paper's energy/load thresholds.

    The base weights are 0.40/0.25/0.20/0.15.  When mean residual energy
    falls below 30%, energy receives an additional 0.15.  When mean
    utilization exceeds 80%, spare capacity receives an additional 0.15.
    The added weight is taken proportionally from deadline and execution,
    then all weights are normalized.
    """
    if not nodes:
        raise ValueError("At least one node is required.")

    energy_levels = [
        node.energy / node.initial_energy if node.initial_energy > 0 else 0.0
        for node in nodes
    ]
    average_energy = sum(energy_levels) / len(energy_levels)

    if current_time is None:
        current_time = max((node.available_time for node in nodes), default=0.0)
    utilizations = [node.utilization(current_time) for node in nodes]
    average_utilization = sum(utilizations) / len(utilizations)

    weights = BASE_WEIGHTS.copy()
    adjustment = 0.0

    if average_energy < ENERGY_THRESHOLD:
        weights["energy"] += ADAPTATION_STEP
        adjustment += ADAPTATION_STEP

    if average_utilization > UTILIZATION_THRESHOLD:
        weights["capacity"] += ADAPTATION_STEP
        adjustment += ADAPTATION_STEP

    if adjustment:
        deadline_take = adjustment * (BASE_WEIGHTS["deadline"] / (BASE_WEIGHTS["deadline"] + BASE_WEIGHTS["execution"]))
        execution_take = adjustment - deadline_take
        weights["deadline"] = max(0.0, weights["deadline"] - deadline_take)
        weights["execution"] = max(0.0, weights["execution"] - execution_take)

    total = sum(weights.values())
    return {key: value / total for key, value in weights.items()}


def _normalise(values):
    low = min(values)
    high = max(values)
    if high - low <= 1e-12:
        return [1.0] * len(values)
    return [(value - low) / (high - low) for value in values]


def _ahdets_pair_score(task, node, current_time, weights, energy_rate):
    execution_time = node.execution_time(task.length)
    predicted_finish = max(current_time, task.arrival_time, node.available_time) + execution_time

    # Paper-defined urgency at the current scheduling time.
    remaining_time = max(task.deadline - current_time, 1e-9)
    deadline = 1.0 / remaining_time

    execution = 1.0 / max(execution_time, 1e-9)

    utilization = node.utilization(max(current_time, 1e-9))
    capacity = 1.0 - utilization

    energy = node.energy / node.initial_energy if node.initial_energy > 0 else 0.0

    return predicted_finish, deadline, execution, capacity, energy


def ahdets_schedule(
    tasks: List[Task],
    nodes: List[EdgeNode],
    weights=None,
    enabled_factors: Optional[Iterable[str]] = None,
    energy_rate: float = 1.0,
) -> List[Tuple[int, int]]:
    """Online AHDETS scheduling with optional factor ablation."""
    if not nodes:
        raise ValueError("At least one node is required.")

    if enabled_factors is None:
        enabled: Set[str] = set(VALID_FACTORS)
    else:
        enabled = set(enabled_factors)

    invalid = enabled - VALID_FACTORS
    if invalid:
        raise ValueError(f"Invalid AHDETS factors: {invalid}")
    if not enabled:
        raise ValueError("At least one AHDETS factor must be enabled.")

    working = _reset_working_nodes(nodes)
    ordered_arrivals = sorted(tasks, key=lambda t: (t.arrival_time, t.task_id))
    pending: List[Task] = []
    next_arrival = 0
    current_time = 0.0
    assignments: List[Tuple[int, int]] = []

    while next_arrival < len(ordered_arrivals) or pending:
        if not pending and next_arrival < len(ordered_arrivals):
            current_time = max(current_time, ordered_arrivals[next_arrival].arrival_time)

        while next_arrival < len(ordered_arrivals) and ordered_arrivals[next_arrival].arrival_time <= current_time + 1e-12:
            pending.append(ordered_arrivals[next_arrival])
            next_arrival += 1

        idle_nodes = [node for node in working if node.available_time <= current_time + 1e-12]
        if not idle_nodes:
            next_free = min(node.available_time for node in working)
            next_arrival_time = ordered_arrivals[next_arrival].arrival_time if next_arrival < len(ordered_arrivals) else float("inf")
            current_time = min(next_free, next_arrival_time)
            continue
        if not pending:
            continue

        adaptive = calculate_adaptive_weights(working, current_time) if weights is None else dict(weights)
        for factor in VALID_FACTORS - enabled:
            adaptive[factor] = 0.0
        total = sum(adaptive.values())
        if total <= 0:
            raise ValueError("Enabled AHDETS factors have zero total weight.")
        adaptive = {key: value / total for key, value in adaptive.items()}

        # Score every pending-task / idle-node pair.  Nodes that can meet the
        # deadline are preferred, exactly as specified by the algorithm.
        pairs = []
        feasible_pairs = []
        for task in pending:
            for node in idle_nodes:
                predicted_finish, deadline, execution, capacity, energy = _ahdets_pair_score(
                    task, node, current_time, adaptive, energy_rate
                )
                pair = {
                    "task": task,
                    "node": node,
                    "finish": predicted_finish,
                    "deadline": deadline,
                    "execution": execution,
                    "capacity": capacity,
                    "energy": energy,
                }
                pairs.append(pair)
                if predicted_finish <= task.deadline + 1e-12 and node.energy + 1e-12 >= node.execution_time(task.length):
                    feasible_pairs.append(pair)

        energy_feasible_pairs = [
            pair for pair in pairs
            if pair["node"].energy + 1e-12 >= pair["node"].execution_time(pair["task"].length)
        ]
        if not energy_feasible_pairs:
            # The workload should remain within the modeled energy budget.
            # If a pathological state occurs, choose the pair with most residual energy.
            energy_feasible_pairs = pairs
        deadline_feasible_pairs = [
            pair for pair in energy_feasible_pairs
            if pair["finish"] <= pair["task"].deadline + 1e-12
        ]
        candidate_pairs = deadline_feasible_pairs if deadline_feasible_pairs else energy_feasible_pairs
        if not candidate_pairs:
            break

        scored = {}
        for factor in ("deadline", "execution", "capacity", "energy"):
            scored[factor] = _normalise([pair[factor] for pair in candidate_pairs])

        best_index = max(
            range(len(candidate_pairs)),
            key=lambda i: (
                sum(adaptive[factor] * scored[factor][i] for factor in VALID_FACTORS),
                -candidate_pairs[i]["finish"],
                -candidate_pairs[i]["task"].deadline,
                -candidate_pairs[i]["task"].task_id,
                -candidate_pairs[i]["node"].node_id,
            ),
        )
        best = candidate_pairs[best_index]
        task = best["task"]
        node = best["node"]

        pending.remove(task)
        assignments.append((task.task_id, node.node_id))
        _reserve(task, node, current_time, energy_rate)

    return assignments
