# AHDETS Architecture

The implementation has four logical layers.

## 1. Task generation layer

`src/task_generator.py` generates heterogeneous computational tasks with Poisson arrivals, uniformly distributed execution lengths, and deadline slack relative to a reference processing capability.

## 2. Scheduling layer

`src/schedulers.py` contains FCFS, SJF, EDF, and AHDETS. All policies operate online: only currently arrived and pending tasks are eligible for a scheduling decision.

AHDETS maintains a temporary copy of node state while producing the dispatch sequence. Node state includes processing capacity, available time, busy time, task count, and residual energy.

## 3. Simulation layer

`src/simulator.py` replays the dispatch sequence deterministically. It enforces arrival-time constraints and serial execution on each node, records task start/finish times, updates node utilization state, and depletes energy.

## 4. Evaluation layer

`src/metrics.py` calculates deadline satisfaction, average response time, capacity-weighted utilization, and total simulated energy consumption. The `experiments/` scripts execute repeated experiments and generate descriptive and statistical analyses.
