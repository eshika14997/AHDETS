from src.models import Task
from src.utils import create_edge_nodes
from src.simulator import Simulator


def test_execute_single_task():

    nodes = create_edge_nodes()

    simulator = Simulator(
        nodes=nodes,
        energy_rate=1.0
    )

    task = Task(
        task_id=1,
        arrival_time=0.0,
        length=1000,
        deadline=5.0
    )

    assignments = [
        (1, 7)
    ]

    tasks, nodes = simulator.run(
        [task],
        assignments
    )

    completed_task = tasks[0]
    node = nodes[6]

    assert completed_task.start_time == 0.0

    # Node 7 has 2000 MIPS.
    # 1000 / 2000 = 0.5 seconds.
    assert completed_task.finish_time == 0.5

    assert completed_task.assigned_node == 7

    assert node.available_time == 0.5
    assert node.busy_time == 0.5
    assert node.total_tasks == 1

    assert node.energy == 99.5


def test_multiple_tasks_on_same_node():

    nodes = create_edge_nodes()

    simulator = Simulator(
        nodes=nodes,
        energy_rate=1.0
    )

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
            length=1000,
            deadline=5.0
        )
    ]

    assignments = [
        (1, 7),
        (2, 7)
    ]

    tasks, nodes = simulator.run(
        tasks,
        assignments
    )

    # Both tasks use Node 7.
    # Each takes 0.5 seconds.
    assert tasks[0].finish_time == 0.5
    assert tasks[1].finish_time == 1.0

    assert nodes[6].available_time == 1.0
    assert nodes[6].busy_time == 1.0
    assert nodes[6].total_tasks == 2