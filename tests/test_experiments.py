from experiments.run_experiments import run_single_experiment
from src.schedulers import fcfs_schedule


def test_single_experiment_runs():
    metrics = run_single_experiment(
        algorithm=fcfs_schedule,
        arrival_rate=0.5,
        seed=42
    )

    assert isinstance(metrics, dict)

    assert "deadline_success_rate" in metrics
    assert "average_response_time" in metrics
    assert "system_utilization" in metrics
    assert "total_energy_consumed" in metrics


def test_metrics_have_valid_values():
    metrics = run_single_experiment(
        algorithm=fcfs_schedule,
        arrival_rate=0.5,
        seed=42
    )

    assert 0.0 <= metrics["deadline_success_rate"] <= 1.0
    assert metrics["average_response_time"] >= 0.0
    assert 0.0 <= metrics["system_utilization"] <= 1.0
    assert metrics["total_energy_consumed"] >= 0.0