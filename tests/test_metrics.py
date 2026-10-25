from src.models import Task
from src.utils import create_edge_nodes
from src.simulator import Simulator

from src.metrics import (
    deadline_success_rate,
    average_response_time,
    system_utilization,
    total_energy_consumed,
    calculate_metrics
)


def test_deadline_success_rate():
    tasks = [
        Task(1, 0.0, 1000, 5.0),
        Task(2, 0.0, 1000, 1.0)
    ]

    tasks[0].finish_time = 2.0
    tasks[1].finish_time = 2.0

    assert deadline_success_rate(tasks) == 0.5


def test_average_response_time():
    tasks = [
        Task(1, 0.0, 1000, 5.0),
        Task(2, 2.0, 1000, 8.0)
    ]

    tasks[0].finish_time = 3.0
    tasks[1].finish_time = 6.0

    assert average_response_time(tasks) == 3.5


def test_system_utilization():
    nodes = create_edge_nodes()

    tasks = [
        Task(1, 0.0, 1000, 10.0)
    ]

    simulator = Simulator(nodes)

    simulator.run(
        tasks,
        [(1, 5)]
    )

    result = system_utilization(tasks, nodes)

    assert result > 0.0
    assert result <= 1.0


def test_total_energy_consumed():
    nodes = create_edge_nodes()

    nodes[0].energy = 90.0
    nodes[1].energy = 80.0

    assert total_energy_consumed(nodes) == 30.0


def test_calculate_metrics():
    nodes = create_edge_nodes()

    tasks = [
        Task(1, 0.0, 1000, 10.0)
    ]

    simulator = Simulator(nodes)

    simulator.run(
        tasks,
        [(1, 5)]
    )

    metrics = calculate_metrics(tasks, nodes)

    assert "deadline_success_rate" in metrics
    assert "average_response_time" in metrics
    assert "system_utilization" in metrics
    assert "total_energy_consumed" in metrics

def test_energy_demand_and_overdraw_are_not_clamped():
    from src.metrics import total_energy_demand, energy_overdraw
    from src.models import EdgeNode

    node = EdgeNode(node_id=1, capacity=1000, initial_energy=10.0)
    node.consume_energy(execution_time=15.0, energy_rate=1.0)

    assert node.energy == 0.0
    assert total_energy_consumed([node]) == 10.0
    assert total_energy_demand([node]) == 15.0
    assert energy_overdraw([node]) == 5.0


def test_energy_demand_reset_by_simulator():
    nodes = create_edge_nodes()
    tasks = [Task(1, 0.0, 1000, 10.0)]
    simulator = Simulator(nodes)
    simulator.run(tasks, [(1, 5)])
    simulator.run(tasks, [(1, 5)])
    assert abs(nodes[4].energy_demand - 1000 / 1500) < 1e-9
