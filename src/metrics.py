from typing import List, Dict
from src.models import Task, EdgeNode


def deadline_success_rate(tasks: List[Task]) -> float:
    """Calculate the fraction of completed tasks that meet their deadlines."""

    completed_tasks = [
        task for task in tasks
        if task.finish_time is not None
    ]

    if not completed_tasks:
        return 0.0

    successful_tasks = sum(
        task.completed_before_deadline
        for task in completed_tasks
    )

    return successful_tasks / len(completed_tasks)


def average_response_time(tasks: List[Task]) -> float:
    """Calculate the average task response time."""

    response_times = [
        task.response_time
        for task in tasks
        if task.response_time is not None
    ]

    if not response_times:
        return 0.0

    return sum(response_times) / len(response_times)


def system_utilization(
    tasks: List[Task],
    nodes: List[EdgeNode]
) -> float:
    """Calculate overall system utilization."""

    if not nodes:
        return 0.0

    finish_times = [
        task.finish_time
        for task in tasks
        if task.finish_time is not None
    ]

    if not finish_times:
        return 0.0

    simulation_end = max(finish_times)

    if simulation_end <= 0:
        return 0.0

    total_busy_time = sum(
        node.busy_time
        for node in nodes
    )

    total_available_time = simulation_end * len(nodes)

    return min(
        total_busy_time / total_available_time,
        1.0
    )


def total_energy_consumed(nodes: List[EdgeNode]) -> float:
    """Calculate total energy consumed by all nodes."""

    return sum(
        node.initial_energy - node.energy
        for node in nodes
    )


def calculate_metrics(
    tasks: List[Task],
    nodes: List[EdgeNode]
) -> Dict[str, float]:
    """Calculate all evaluation metrics."""

    return {
        "deadline_success_rate": deadline_success_rate(tasks),
        "average_response_time": average_response_time(tasks),
        "system_utilization": system_utilization(tasks, nodes),
        "total_energy_consumed": total_energy_consumed(nodes)
    }