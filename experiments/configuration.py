# Number of tasks in each independent simulation run.
NUM_TASKS = 1000

# Arrival rates chosen from the actual aggregate cluster capacity.
# With mean task length ~1025 MI and aggregate capacity 16,250 MIPS,
# these correspond to approximately 19%, 76%, and 114% offered load.
WORKLOADS = {
    "light": 3.0,
    "moderate": 12.0,
    "heavy": 18.0,
}

NUM_RUNS = 30
BASE_SEED = 42
