import pandas as pd
import random
import math
import sys
import os


# Task workload is integer in [1,MAX_WORKLOAD]
MAX_WORKLOAD = 100
# Task types according to epEBench benchmark, cf. https://doi.org/10.1109/PDP.2017.21 and https://github.com/RobertMueller/epEBench.
# TASKTYPES = ['MEMORY', 'BRANCH', 'FMULT', 'SIMD', 'MATMUL']
TASKTYPES = ['MEMORY', 'FMULT', 'SIMD']
# PRNG seed value
RANDSEED = 2502


# Parameters: output path for task sets, number of tasks, number of cores, number of task sets to be created
def main():
    if len(sys.argv) < 5:
        print("Please specify output path, number of tasks, number of cores, and number of task sets to be created. Exiting...")
        sys.exit(0)
    random.seed(RANDSEED)
    output_path = sys.argv[1]
    num_tasks = int(sys.argv[2])
    num_cores = int(sys.argv[3])
    num_tasksets = int(sys.argv[4])
    for i in range(num_tasksets):
        ts_ids = [None] * num_tasks
        ts_workloads = [None] * num_tasks
        ts_max_widths = [None] * num_tasks
        ts_tasktypes = [None] * num_tasks
        # Create tasks
        for j in range(num_tasks):
            ts_ids[j] = j
            if j == 0:
                ts_workloads[j] = random.choice(range(1, MAX_WORKLOAD // 10))
            else:
                ts_workloads[j] = random.choice(range(1,MAX_WORKLOAD+1))
            ts_tasktypes[j] = random.choice(TASKTYPES)
            max_width_log = (random.choice(range(int(math.log2(num_cores))+1)))
            ts_max_widths[j] = 2**max_width_log
            while ts_workloads[j] / ts_max_widths[j] > MAX_WORKLOAD/(num_cores/2):
                # Obtain new values to avoid tasks with huge workloads and small maximum width (obviously, this leads to skewed distribution)
                if j == 0:
                    ts_workloads[j] = random.choice(range(1, MAX_WORKLOAD//10))
                else:
                    ts_workloads[j] = random.choice(range(1,MAX_WORKLOAD+1))
                max_width_log = (random.choice(range(int(math.log2(num_cores))+1)))
                ts_max_widths[j] = 2**max_width_log
        # Collect in data frame and write to file
        df = pd.DataFrame()
        df['id'] = ts_ids
        df['workload'] = ts_workloads
        df['max_width'] = ts_max_widths
        df['tasktype'] = ts_tasktypes
        filename = "taskset_n" + str(num_tasks) + "_" + str(i+1) + ".csv"
        if not os.path.isdir(output_path):
            os.mkdir(output_path)
        df.to_csv(os.path.join(output_path, filename), index=False)


if __name__ == "__main__":
    main()