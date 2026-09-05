from src.task_generator import generate_tasks


def test_generate_tasks():
    tasks = generate_tasks(
        num_tasks=10,
        arrival_rate=1.0,
        seed=42
    )

    assert len(tasks) == 10


def test_task_lengths_are_in_range():
    tasks = generate_tasks(
        num_tasks=100,
        arrival_rate=1.0,
        min_length=50,
        max_length=2000,
        seed=42
    )

    for task in tasks:
        assert 50 <= task.length <= 2000


def test_arrival_times_are_increasing():
    tasks = generate_tasks(
        num_tasks=100,
        arrival_rate=1.0,
        seed=42
    )

    for i in range(1, len(tasks)):
        assert tasks[i].arrival_time >= tasks[i - 1].arrival_time


def test_deadlines_are_after_arrival():
    tasks = generate_tasks(
        num_tasks=100,
        arrival_rate=1.0,
        seed=42
    )

    for task in tasks:
        assert task.deadline > task.arrival_time


def test_reproducibility():
    tasks1 = generate_tasks(
        num_tasks=10,
        arrival_rate=1.0,
        seed=42
    )

    tasks2 = generate_tasks(
        num_tasks=10,
        arrival_rate=1.0,
        seed=42
    )

    for task1, task2 in zip(tasks1, tasks2):
        assert task1.arrival_time == task2.arrival_time
        assert task1.length == task2.length
        assert task1.deadline == task2.deadline