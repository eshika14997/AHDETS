from src.models import Task
from src.utils import create_edge_nodes
from src.schedulers import fcfs_schedule


def test_fcfs_returns_assignment_for_every_task():

    nodes = create_edge_nodes()

    tasks = [
        Task(
            task_id=1,
            arrival_time=0.0,
            length=1000,
            deadline=5.0
        ),
        Task(
            task_id=2,
            arrival_time=1.0,
            length=500,
            deadline=5.0
        ),
        Task(
            task_id=3,
            arrival_time=2.0,
            length=1500,
            deadline=6.0
        )
    ]

    assignments = fcfs_schedule(tasks, nodes)

    assert len(assignments) == 3

    assigned_task_ids = [
        assignment[0]
        for assignment in assignments
    ]

    assert assigned_task_ids == [1, 2, 3]


def test_fcfs_assigns_valid_nodes():

    nodes = create_edge_nodes()

    tasks = [
        Task(
            task_id=1,
            arrival_time=0.0,
            length=1000,
            deadline=5.0
        ),
        Task(
            task_id=2,
            arrival_time=1.0,
            length=500,
            deadline=5.0
        )
    ]

    assignments = fcfs_schedule(tasks, nodes)

    valid_node_ids = {
        node.node_id
        for node in nodes
    }

    for task_id, node_id in assignments:
        assert node_id in valid_node_ids


def test_fcfs_respects_arrival_order():

    nodes = create_edge_nodes()

    tasks = [
        Task(
            task_id=3,
            arrival_time=3.0,
            length=500,
            deadline=6.0
        ),
        Task(
            task_id=1,
            arrival_time=1.0,
            length=500,
            deadline=4.0
        ),
        Task(
            task_id=2,
            arrival_time=2.0,
            length=500,
            deadline=5.0
        )
    ]

    assignments = fcfs_schedule(tasks, nodes)

    assigned_task_ids = [
        task_id
        for task_id, node_id in assignments
    ]

    assert assigned_task_ids == [1, 2, 3]

from src.schedulers import sjf_schedule


def test_sjf_returns_assignment_for_every_task():

    nodes = create_edge_nodes()

    tasks = [
        Task(
            task_id=1,
            arrival_time=0.0,
            length=1500,
            deadline=10.0
        ),
        Task(
            task_id=2,
            arrival_time=0.0,
            length=500,
            deadline=5.0
        ),
        Task(
            task_id=3,
            arrival_time=0.0,
            length=1000,
            deadline=8.0
        )
    ]

    assignments = sjf_schedule(tasks, nodes)

    assert len(assignments) == 3


def test_sjf_orders_tasks_by_length():

    nodes = create_edge_nodes()

    tasks = [
        Task(
            task_id=1,
            arrival_time=0.0,
            length=1500,
            deadline=10.0
        ),
        Task(
            task_id=2,
            arrival_time=0.0,
            length=500,
            deadline=5.0
        ),
        Task(
            task_id=3,
            arrival_time=0.0,
            length=1000,
            deadline=8.0
        )
    ]

    assignments = sjf_schedule(tasks, nodes)

    assigned_task_ids = [
        task_id
        for task_id, node_id in assignments
    ]

    assert assigned_task_ids == [2, 3, 1]


def test_sjf_assigns_valid_nodes():

    nodes = create_edge_nodes()

    tasks = [
        Task(
            task_id=1,
            arrival_time=0.0,
            length=1000,
            deadline=5.0
        ),
        Task(
            task_id=2,
            arrival_time=0.0,
            length=500,
            deadline=5.0
        )
    ]

    assignments = sjf_schedule(tasks, nodes)

    valid_node_ids = {
        node.node_id
        for node in nodes
    }

    for task_id, node_id in assignments:
        assert node_id in valid_node_ids

from src.schedulers import edf_schedule


def test_edf_returns_assignment_for_every_task():
    nodes = create_edge_nodes()

    tasks = [
        Task(task_id=1, arrival_time=0.0, length=1500, deadline=10.0),
        Task(task_id=2, arrival_time=0.0, length=500, deadline=5.0),
        Task(task_id=3, arrival_time=0.0, length=1000, deadline=8.0)
    ]

    assignments = edf_schedule(tasks, nodes)

    assert len(assignments) == 3


def test_edf_orders_tasks_by_deadline():
    nodes = create_edge_nodes()

    tasks = [
        Task(task_id=1, arrival_time=0.0, length=1500, deadline=10.0),
        Task(task_id=2, arrival_time=0.0, length=500, deadline=5.0),
        Task(task_id=3, arrival_time=0.0, length=1000, deadline=8.0)
    ]

    assignments = edf_schedule(tasks, nodes)

    assigned_task_ids = [task_id for task_id, node_id in assignments]

    assert assigned_task_ids == [2, 3, 1]


def test_edf_assigns_valid_nodes():
    nodes = create_edge_nodes()

    tasks = [
        Task(task_id=1, arrival_time=0.0, length=1000, deadline=8.0),
        Task(task_id=2, arrival_time=0.0, length=500, deadline=5.0)
    ]

    assignments = edf_schedule(tasks, nodes)

    valid_node_ids = {node.node_id for node in nodes}

    for task_id, node_id in assignments:
        assert node_id in valid_node_ids


from src.schedulers import ahdets_schedule


def test_ahdets_returns_assignment_for_every_task():
    nodes = create_edge_nodes()

    tasks = [
        Task(task_id=1, arrival_time=0.0, length=1500, deadline=10.0),
        Task(task_id=2, arrival_time=0.0, length=500, deadline=5.0),
        Task(task_id=3, arrival_time=0.0, length=1000, deadline=8.0)
    ]

    assignments = ahdets_schedule(tasks, nodes)

    assert len(assignments) == 3


def test_ahdets_assigns_valid_nodes():
    nodes = create_edge_nodes()

    tasks = [
        Task(task_id=1, arrival_time=0.0, length=1000, deadline=8.0),
        Task(task_id=2, arrival_time=0.0, length=500, deadline=5.0)
    ]

    assignments = ahdets_schedule(tasks, nodes)

    valid_node_ids = {node.node_id for node in nodes}

    for task_id, node_id in assignments:
        assert node_id in valid_node_ids


def test_ahdets_uses_all_tasks():
    nodes = create_edge_nodes()

    tasks = [
        Task(task_id=1, arrival_time=0.0, length=1000, deadline=8.0),
        Task(task_id=2, arrival_time=1.0, length=1500, deadline=10.0),
        Task(task_id=3, arrival_time=2.0, length=500, deadline=6.0)
    ]

    assignments = ahdets_schedule(tasks, nodes)

    assigned_task_ids = {
        task_id for task_id, node_id in assignments
    }

    assert assigned_task_ids == {1, 2, 3}

from src.schedulers import calculate_adaptive_weights


def test_adaptive_weights_sum_to_one():
    nodes = create_edge_nodes()

    weights = calculate_adaptive_weights(nodes)

    total = sum(weights.values())

    assert abs(total - 1.0) < 1e-9


def test_adaptive_weights_have_all_factors():
    nodes = create_edge_nodes()

    weights = calculate_adaptive_weights(nodes)

    assert "deadline" in weights
    assert "execution" in weights
    assert "capacity" in weights
    assert "energy" in weights


def test_low_energy_increases_energy_weight():
    nodes = create_edge_nodes()

    for node in nodes:
        node.energy = 20.0

    weights = calculate_adaptive_weights(nodes)

    assert weights["energy"] > 0.15


def test_high_utilization_increases_capacity_weight():
    nodes = create_edge_nodes()

    for node in nodes:
        node.busy_time = 100.0
        node.available_time = 100.0

    weights = calculate_adaptive_weights(nodes)

    assert weights["capacity"] > 0.20