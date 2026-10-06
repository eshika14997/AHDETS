# AHDETS

Adaptive Heuristic-Based Deadline and Energy-Aware Task Scheduling for Heterogeneous Edge Computing Systems.

This repository contains a reproducible simulation implementation of AHDETS and three baseline schedulers: FCFS, SJF, and EDF.

## Experimental design

- 10 heterogeneous edge nodes: 500--3000 MIPS
- Initial node energy: 100 simulated units
- 1,000 tasks per simulation run
- Task length: 50--2,000 MI
- Deadline slack: 1.5x--5x expected execution time on a 1,500-MIPS reference node
- Poisson task arrivals
- 30 independent seeds per algorithm/workload
- Workloads are calibrated from the cluster's aggregate capacity:
  - Light: lambda = 3 tasks/s (~19% offered load)
  - Moderate: lambda = 12 tasks/s (~76% offered load)
  - Heavy: lambda = 18 tasks/s (~114% offered load)

The schedulers make online decisions using only tasks that have arrived by the current decision time. The dispatch sequence is replayed by the deterministic simulator to compute task completion times, deadline satisfaction, utilization, and energy consumption.

## Algorithms

### FCFS
Selects the earliest-arriving pending task and assigns it to the idle node with the earliest completion time.

### SJF
Selects the shortest pending task at each scheduling decision and assigns it to the idle node with the earliest completion time.

### EDF
Selects the pending task with the earliest absolute deadline and assigns it to the idle node with the earliest completion time.

### AHDETS
Evaluates pending task/idle-node pairs using four normalized factors:

- deadline urgency: `1 / (deadline - current_time)`
- execution efficiency: inverse predicted execution time
- spare capacity: `1 - utilization`
- residual energy: remaining energy fraction

The base weights are 0.40, 0.25, 0.20, and 0.15. Weight adaptation increases the energy weight when mean residual energy falls below 30% and the capacity weight when mean utilization exceeds 80%; the added weight is taken proportionally from the deadline and execution factors.

AHDETS first prefers feasible task/node pairs whose predicted completion meets the task deadline. If no such pair exists, it selects from energy-feasible pairs so that the simulation remains work-conserving.

## Metrics

- **Deadline Satisfaction Ratio (DSR):** fraction of completed tasks finishing by their absolute deadline.
- **Average Response Time:** mean completion time minus arrival time.
- **System Utilization:** capacity-weighted active processing time divided by total available capacity-time over the experiment makespan.
- **Total Energy Consumption:** cumulative energy depleted from all nodes.

Energy is a simplified simulation model: computation consumes energy at a fixed rate of one simulated energy unit per second of execution. It is not a measurement of physical hardware power consumption.

## Reproduce the experiments

Create/activate a Python environment and install the dependencies:

```text
pip install -r requirements.txt
```

Run the main benchmark:

```text
python experiments/run_experiments.py
python experiments/analyze_results.py
python experiments/statistical_tests.py
```

Run the component ablation study:

```text
python experiments/run_ablation.py
python experiments/analyze_ablation.py
```

Run the tests:

```text
python -m pytest
```

The statistical analyses use paired Wilcoxon signed-rank tests and Holm-Bonferroni correction. Cohen's dz is reported as the paired effect size.

## Reproducibility

All repeated experiments use the same seed sequence (`42` through `71`) across algorithms and ablation variants, allowing paired comparisons on identical generated workloads.

Generated raw data, summary tables, statistical tables, and plots are stored under `results/`.
