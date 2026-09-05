import numpy as np

from src.models import Task


def generate_tasks(
    num_tasks: int,
    arrival_rate: float,
    min_length: float = 50.0,
    max_length: float = 2000.0,
    min_slack: float = 1.5,
    max_slack: float = 5.0,
    reference_capacity: float = 1500.0,
    seed = None,
):
    """
    Generate computational tasks for the AHDETS simulation.

    Parameters
    ----------
    num_tasks : int
        Number of tasks to generate.

    arrival_rate : float
        Average task arrival rate per second.

    min_length : float
        Minimum task length in MI.

    max_length : float
        Maximum task length in MI.

    min_slack : float
        Minimum deadline slack multiplier.

    max_slack : float
        Maximum deadline slack multiplier.

    reference_capacity : float
        Reference processing capacity in MIPS used
        to estimate a task's expected execution time.

    seed : int or None
        Random seed for reproducible experiments.

    Returns
    -------
    list[Task]
        Generated tasks.
    """

    if num_tasks <= 0:
        raise ValueError("num_tasks must be greater than 0.")

    if arrival_rate <= 0:
        raise ValueError("arrival_rate must be greater than 0.")

    if min_length <= 0 or max_length < min_length:
        raise ValueError("Invalid task length range.")

    if min_slack <= 0 or max_slack < min_slack:
        raise ValueError("Invalid deadline slack range.")

    if reference_capacity <= 0:
        raise ValueError("reference_capacity must be greater than 0.")

    rng = np.random.default_rng(seed)

    # Poisson arrivals:
    # Inter-arrival times follow an exponential distribution.
    inter_arrival_times = rng.exponential(
        scale=1.0 / arrival_rate,
        size=num_tasks
    )

    arrival_times = np.cumsum(inter_arrival_times)

    # Task lengths in MI.
    lengths = rng.uniform(
        min_length,
        max_length,
        size=num_tasks
    )

    # Expected execution time using a reference node.
    expected_execution_times = lengths / reference_capacity

    # Deadline slack multiplier.
    slack = rng.uniform(
        min_slack,
        max_slack,
        size=num_tasks
    )

    # Absolute deadline.
    deadlines = arrival_times + (
        expected_execution_times * slack
    )

    tasks = []

    for i in range(num_tasks):
        task = Task(
            task_id=i + 1,
            arrival_time=float(arrival_times[i]),
            length=float(lengths[i]),
            deadline=float(deadlines[i])
        )

        tasks.append(task)

    return tasks