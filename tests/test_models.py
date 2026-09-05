from src.models import Task, EdgeNode
from src.utils import create_edge_nodes

def test_task_creation():
    task = Task(
        task_id=1,
        arrival_time=0.0,
        length=1000,
        deadline=5.0
    )

    assert task.task_id == 1
    assert task.length == 1000
    assert task.deadline == 5.0
    assert task.start_time is None
    assert task.finish_time is None


def test_task_response_time():
    task = Task(
        task_id=1,
        arrival_time=2.0,
        length=1000,
        deadline=10.0
    )

    task.start_time = 3.0
    task.finish_time = 5.0

    assert task.response_time == 3.0


def test_task_deadline():
    task = Task(
        task_id=1,
        arrival_time=0.0,
        length=1000,
        deadline=5.0
    )

    task.finish_time = 4.0

    assert task.completed_before_deadline is True


def test_node_creation():
    node = EdgeNode(
        node_id=1,
        capacity=1000
    )

    assert node.node_id == 1
    assert node.capacity == 1000
    assert node.energy == 100.0


def test_execution_time():
    node = EdgeNode(
        node_id=1,
        capacity=2000
    )

    execution_time = node.execution_time(1000)

    assert execution_time == 0.5


def test_energy_consumption():
    node = EdgeNode(
        node_id=1,
        capacity=1000
    )

    node.consume_energy(
        execution_time=2.0,
        energy_rate=5.0
    )

    assert node.energy == 90.0
    from src.utils import create_edge_nodes


def test_create_edge_nodes():
    nodes = create_edge_nodes()

    assert len(nodes) == 10


def test_node_capacities():
    nodes = create_edge_nodes()

    capacities = [node.capacity for node in nodes]

    assert capacities == [
        500,
        750,
        1000,
        1250,
        1500,
        1750,
        2000,
        2250,
        2500,
        3000
    ]


def test_initial_node_energy():
    nodes = create_edge_nodes()

    for node in nodes:
        assert node.energy == 100.0