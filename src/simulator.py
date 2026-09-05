from typing import List, Tuple

from src.models import Task, EdgeNode


class Simulator:
    """
    Discrete-event simulator for heterogeneous edge computing.
    """

    def __init__(
        self,
        nodes: List[EdgeNode],
        energy_rate: float = 1.0
    ):
        self.nodes = nodes
        self.energy_rate = energy_rate

    def reset_nodes(self):
        """
        Reset all nodes to their initial state.
        """

        for node in self.nodes:
            node.energy = node.initial_energy
            node.available_time = 0.0
            node.busy_time = 0.0
            node.total_tasks = 0

    def reset_tasks(self, tasks: List[Task]):
        """
        Reset scheduling information for all tasks.
        """

        for task in tasks:
            task.start_time = None
            task.finish_time = None
            task.assigned_node = None

    def execute_task(
        self,
        task: Task,
        node: EdgeNode,
        current_time: float
    ):
        """
        Execute one task on one node.
        """

        # A node cannot start before:
        # 1. The task arrives.
        # 2. The node becomes available.
        start_time = max(
            task.arrival_time,
            node.available_time,
            current_time
        )

        execution_time = node.execution_time(task.length)

        finish_time = start_time + execution_time

        # Store task information.
        task.start_time = start_time
        task.finish_time = finish_time
        task.assigned_node = node.node_id

        # Update node state.
        node.available_time = finish_time
        node.busy_time += execution_time
        node.total_tasks += 1

        # Consume energy.
        node.consume_energy(
            execution_time,
            self.energy_rate
        )

        return finish_time

    def run(
        self,
        tasks: List[Task],
        assignments: List[Tuple[int, int]]
    ):
        """
        Run the simulation.

        Parameters
        ----------
        tasks:
            List of Task objects.

        assignments:
            List of tuples:

                (task_id, node_id)

        Returns
        -------
        tasks, nodes
            Updated tasks and nodes.
        """

        # Always start with a clean system.
        self.reset_nodes()
        self.reset_tasks(tasks)

        task_lookup = {
            task.task_id: task
            for task in tasks
        }

        node_lookup = {
            node.node_id: node
            for node in self.nodes
        }

        # Process assignments in the order supplied
        # by the scheduler.
        for task_id, node_id in assignments:

            if task_id not in task_lookup:
                raise ValueError(
                    f"Task {task_id} does not exist."
                )

            if node_id not in node_lookup:
                raise ValueError(
                    f"Node {node_id} does not exist."
                )

            task = task_lookup[task_id]
            node = node_lookup[node_id]

            self.execute_task(
                task,
                node,
                task.arrival_time
            )

        return tasks, self.nodes