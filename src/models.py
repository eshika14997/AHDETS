from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    """
    Represents a computational task arriving at the edge system.
    """

    task_id: int
    arrival_time: float
    length: float
    deadline: float

    start_time: Optional[float] = None
    finish_time: Optional[float] = None
    assigned_node: Optional[int] = None

    @property
    def response_time(self) -> Optional[float]:
        """Return response time after the task has finished."""
        if self.finish_time is None:
            return None

        return self.finish_time - self.arrival_time

    @property
    def completed_before_deadline(self) -> Optional[bool]:
        """Check whether the task finished before its deadline."""
        if self.finish_time is None:
            return None

        return self.finish_time <= self.deadline


@dataclass
class EdgeNode:
    """
    Represents a heterogeneous edge computing node.
    """

    node_id: int
    capacity: float
    initial_energy: float = 100.0

    energy: float = field(init=False)
    available_time: float = 0.0
    busy_time: float = 0.0
    total_tasks: int = 0

    def __post_init__(self):
        self.energy = self.initial_energy

    def execution_time(self, task_length: float) -> float:
        """
        Calculate execution time for a task.

        execution time = task length / node processing capacity
        """
        return task_length / self.capacity

    def utilization(self, current_time: float) -> float:
        """
        Calculate current node utilization.

        Returns a value between 0 and 1.
        """
        if current_time <= 0:
            return 0.0

        return min(self.busy_time / current_time, 1.0)

    def consume_energy(self, execution_time: float, energy_rate: float):
        """
        Reduce node energy after executing a task.
        """
        energy_used = execution_time * energy_rate
        self.energy = max(0.0, self.energy - energy_used)