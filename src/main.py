import pandas as pd

from optimizer.ILP.baseOptimizer import BaseOptimizer
from optimizer.ILP.relaxedOptimizer import RelaxedOptimizer
from optimizer.ILP.symmetryBaseOptimizer import SymmetryBaseOptimizer
from optimizer.ILP.symmetryRelaxedOptimizer import SymmetryRelaxedOptimizer
from optimizer.heuristic.baseHeuristic import Heuristic
from optimizer.heuristic.relaxedHeuristic import RelaxedHeuristic
from data.Environments.default import env as default_base_env
from data.Environments.new_default import env as new_default_base_env
from data.Environments.default_small import env as default_base_small_env
from data.Environments.new_default_small import env as new_default_base_small_env
from data.Environments.relaxed_small import env as default_relaxed_small_env
from data.Environments.new_relaxed_small import env as new_default_relaxed_small_env
from data.Environments.relaxed import env as default_relaxed_env
from data.Environments.new_relaxed import env as new_default_relaxed_env
from data.Environments.symmetry_default import env as symmetry_base_env
from data.Environments.symmetry_relaxed import env as symmetry_relaxed_env

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

    # base_env = default_base_env
    base_env = new_default_base_env
    # relaxed_env = default_relaxed_env
    relaxed_env = new_default_relaxed_env

    if env_size == "small":
        # base_env = default_base_small_env
        base_env = new_default_base_small_env
        # relaxed_env = default_relaxed_small_env
        relaxed_env = new_default_relaxed_small_env

    task_graph = igraph.load(input_filename)

    if optimizer_type == "Relaxed":
        optimizer = RelaxedOptimizer(task_graph, relaxed_env["compute_resources"], relaxed_env["network"],
                                     relaxed_env["execution_time_multipliers"], relaxed_env["power"])

    elif optimizer_type == "SymmetryBase":
        optimizer = SymmetryBaseOptimizer(task_graph, symmetry_base_env["compute_resources"],
                                          symmetry_base_env["network"],
                                          symmetry_base_env["execution_time_multipliers"], symmetry_base_env["power"],
                                          symmetry_relaxed_env["level"])

    elif optimizer_type == "SymmetryRelaxed":
        optimizer = SymmetryRelaxedOptimizer(task_graph, symmetry_relaxed_env["compute_resources"],
                                             symmetry_relaxed_env["network"],
                                             symmetry_relaxed_env["execution_time_multipliers"],
                                             symmetry_relaxed_env["power"], symmetry_relaxed_env["level"])

    elif optimizer_type == "BaseHeuristic":
        optimizer = Heuristic(task_graph, base_env["compute_resources"],
                                             base_env["network"],
                                             base_env["execution_time_multipliers"],
                                             base_env["power"])
    elif optimizer_type == "RelaxedHeuristic":
        optimizer = RelaxedHeuristic(task_graph, relaxed_env["compute_resources"], relaxed_env["network"], relaxed_env["execution_time_multipliers"], relaxed_env["power"])

    else:
        # optimizer = BaseOptimizer(task_graph, default_env["compute_resources"], default_env["network"], default_env["execution_time_multipliers"], default_env["power"])
        optimizer = BaseOptimizer(task_graph, base_env["compute_resources"], base_env["network"], base_env["execution_time_multipliers"], base_env["power"])

    optimizer.compute_deadline()

    start_time = time.process_time()
    status = optimizer.optimize()
    end_time = time.process_time()

    print("Optimization (" + optimizer_type + ") Time: " + str(end_time - start_time))

    time_dict = {"Time": [end_time - start_time]}
    time_df = pd.DataFrame(time_dict)

    time_df.to_csv(output_path + "/time.csv")
    if status != -1:
        optimizer.generate_result(output_path)

    if optimizer_type == "SymmetryBase" or optimizer_type == "SymmetryRelaxed":
        optimizer.data_completer(output_path)
