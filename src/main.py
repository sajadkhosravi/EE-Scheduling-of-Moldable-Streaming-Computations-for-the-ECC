import pandas as pd

from optimizer.ILP.strictOptimizer import BaseOptimizer
from optimizer.ILP.relaxedOptimizer import RelaxedOptimizer
from optimizer.heuristic.strictHeuristic import Heuristic
from optimizer.heuristic.relaxedHeuristic import RelaxedHeuristic
from data.Environments.default import env as default_base_env
from data.Environments.default_small import env as default_base_small_env
from data.Environments.default_large import env as default_base_large_env
from data.Environments.relaxed_small import env as default_relaxed_small_env
from data.Environments.relaxed_large import env as default_relaxed_large_env
from data.Environments.relaxed import env as default_relaxed_env

import sys
import igraph
import time

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("Please specify optimizer type, env size, task set file (including path), and path to results directory!")
        sys.exit(1)

    optimizer_type = sys.argv[1]
    env_size = sys.argv[2]
    input_filename = sys.argv[3]
    output_path = sys.argv[4]

    base_env = default_base_env
    relaxed_env = default_relaxed_env

    if env_size == "Small":
        base_env = default_base_small_env
        relaxed_env = default_relaxed_small_env

    elif env_size == "Large":
        base_env = default_base_large_env
        relaxed_env = default_relaxed_large_env

    task_graph = igraph.load(input_filename)

    if optimizer_type == "Relaxed":
        optimizer = RelaxedOptimizer(task_graph, relaxed_env["compute_resources"], relaxed_env["network"],
                                     relaxed_env["execution_time_multipliers"], relaxed_env["power"])

    elif optimizer_type == "StrictHeuristic":
        optimizer = Heuristic(task_graph, base_env["compute_resources"],
                                             base_env["network"],
                                             base_env["execution_time_multipliers"],
                                             base_env["power"])
    elif optimizer_type == "RelaxedHeuristic":
        optimizer = RelaxedHeuristic(task_graph, relaxed_env["compute_resources"], relaxed_env["network"], relaxed_env["execution_time_multipliers"], relaxed_env["power"])

    else:
        optimizer = BaseOptimizer(task_graph, base_env["compute_resources"], base_env["network"], base_env["execution_time_multipliers"], base_env["power"])

    optimizer.compute_deadline()

    start_time = time.perf_counter()
    status = optimizer.optimize()
    end_time = time.perf_counter()

    print("Optimization (" + optimizer_type + ") Time: " + str(end_time - start_time))

    result_status = -1
    if status != -1:
        status = optimizer.generate_result(output_path)

    time_dict = {"Time": [end_time - start_time], "status": status}
    time_df = pd.DataFrame(time_dict)

    time_df.to_csv(output_path + "/time.csv")
