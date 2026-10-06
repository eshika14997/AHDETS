# Experimental Methodology

## 1. Simulation model

The experiment models a heterogeneous edge cluster containing ten nodes with processing capacities of 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, and 3000 MIPS. Every node starts with 100 simulated energy units.

A task is represented by arrival time, computational length in MI, and an absolute deadline. Task lengths are sampled uniformly from 50 to 2,000 MI. Inter-arrival times follow an exponential distribution, producing a Poisson arrival process. Deadline slack is sampled uniformly from 1.5x to 5x the execution time expected on a 1,500-MIPS reference node.

## 2. Workload calibration

The aggregate processing capacity is 16,250 MIPS. The mean generated task length is approximately 1,025 MI, so the approximate offered computational load is:

`rho ~= lambda * 1025 / 16250`

The selected arrival rates therefore represent approximately:

| Workload | Arrival rate | Approx. offered load |
|---|---:|---:|
| Light | 3 tasks/s | 19% |
| Moderate | 12 tasks/s | 76% |
| Heavy | 18 tasks/s | 114% |

Each workload contains 1,000 tasks per run and is repeated for 30 seeds (`42`--`71`).

## 3. Online scheduling model

Scheduling decisions are made online. Tasks become eligible for scheduling only after their arrival time. At each decision point, the scheduler considers the currently pending tasks and idle nodes. A decision is made whenever a task arrives or a node becomes available, producing a work-conserving non-preemptive dispatch sequence.

This avoids giving SJF, EDF, or AHDETS knowledge of future task arrivals. The simulator then replays the dispatch sequence in order, respecting task arrival times and node availability, and records the resulting completion times and node state.

## 4. Baseline policies

- **FCFS:** earliest-arriving pending task first.
- **SJF:** shortest pending task first.
- **EDF:** earliest absolute deadline first.

For each selected task, the baseline policies use the idle node with the earliest predicted completion time.

## 5. AHDETS heuristic

For each pending task and idle node, AHDETS computes four normalized factors:

`D = 1 / (d_i - t)`

`X = 1 / (l_i / C_j)`

`C = 1 - U_j(t)`

`E = E_j(t) / E_j(0)`

The priority score is:

`P(t_i,n_j) = w_D D + w_X X + w_C C + w_E E`

The base weights are 0.40, 0.25, 0.20, and 0.15. Mean residual energy below 30% increases the energy weight by 0.15, while mean utilization above 80% increases the spare-capacity weight by 0.15. The additional weight is removed proportionally from the deadline and execution terms, followed by normalization.

Before scoring, AHDETS prefers pairs that are both energy-feasible and predicted to complete by the deadline. If no deadline-feasible pair exists, it selects from energy-feasible pairs and therefore continues to execute the workload while exposing deadline-miss risk through the final metrics.

## 6. Energy model

Energy consumption is modeled as:

`energy_used = execution_time * energy_rate`

with `energy_rate = 1` simulated energy unit per second. The model is intentionally simple and represents computational energy depletion rather than physical electrical power. Consequently, the energy metric should be interpreted as a simulation quantity, not as joules or a hardware measurement.

## 7. Performance metrics

### Deadline Satisfaction Ratio

`DSR = tasks completed by deadline / completed tasks`

### Average Response Time

`mean(finish_time - arrival_time)`

### System Utilization

Utilization is capacity-weighted:

`U = sum(C_j * busy_time_j) / (sum(C_j) * makespan)`

### Total Energy Consumption

`E_total = sum(initial_energy_j - residual_energy_j)`

## 8. Statistical analysis

The same seed is used across all algorithms for each workload, producing paired observations. Thirty runs are used per workload/algorithm combination. Descriptive results report mean, standard deviation, and 95% t-based confidence intervals.

Pairwise AHDETS-versus-baseline comparisons use two-sided paired Wilcoxon signed-rank tests. Because multiple hypotheses are tested, p-values are adjusted using Holm-Bonferroni correction across the complete set of 36 main comparisons. Cohen's dz is reported as the paired effect size.

The ablation study contains four component-removal variants: No Deadline, No Execution, No Capacity, and No Energy. These produce 48 paired metric comparisons, corrected jointly using Holm-Bonferroni.

## 9. Reproducibility

The complete workload generation, scheduling, simulation, analysis, and statistical-testing scripts are included in the repository. Raw experiment data and generated tables/plots are stored under `results/`.
