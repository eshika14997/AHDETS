from typing import Dict, List

from src.models import EdgeNode, Task


def deadline_success_rate(tasks: List[Task]) -> float:
    completed = [task for task in tasks if task.finish_time is not None]
    if not completed:
        return 0.0
    return sum(bool(task.completed_before_deadline) for task in completed) / len(completed)


def average_response_time(tasks: List[Task]) -> float:
    response_times = [task.response_time for task in tasks if task.response_time is not None]
    return sum(response_times) / len(response_times) if response_times else 0.0


def system_utilization(tasks: List[Task], nodes: List[EdgeNode]) -> float:
    """Capacity-weighted utilization over the experiment makespan."""
    if not nodes:
        return 0.0
    finish_times = [task.finish_time for task in tasks if task.finish_time is not None]
    if not finish_times:
        return 0.0
    simulation_end = max(finish_times)
    total_capacity = sum(node.capacity for node in nodes)
    if simulation_end <= 0 or total_capacity <= 0:
        return 0.0
    active_capacity_time = sum(node.capacity * node.busy_time for node in nodes)
    return min(active_capacity_time / (total_capacity * simulation_end), 1.0)


def total_energy_consumed(nodes: List[EdgeNode]) -> float:
    return sum(node.initial_energy - node.energy for node in nodes)


def total_energy_demand(nodes: List[EdgeNode]) -> float:
    """Energy required by all executed work, ignoring the per-node budget cap."""
    return sum(node.energy_demand for node in nodes)


def energy_overdraw(nodes: List[EdgeNode]) -> float:
    """Energy demanded beyond each node's initial budget.

    ``total_energy_consumed`` is capped at the budget because node energy is
    clamped at zero.  A positive overdraw means the schedule kept running work
    on nodes that had already exhausted their simulated energy.
    """
    return sum(max(0.0, node.energy_demand - node.initial_energy) for node in nodes)


def calculate_metrics(tasks: List[Task], nodes: List[EdgeNode]) -> Dict[str, float]:
    return {
        "deadline_success_rate": deadline_success_rate(tasks),
        "average_response_time": average_response_time(tasks),
        "system_utilization": system_utilization(tasks, nodes),
        "total_energy_consumed": total_energy_consumed(nodes),
        "total_energy_demand": total_energy_demand(nodes),
        "energy_overdraw": energy_overdraw(nodes),
    }
