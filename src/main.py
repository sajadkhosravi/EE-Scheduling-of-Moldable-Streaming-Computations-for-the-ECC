import pandas as pd

from optimizer.ILP.baseOptimizer import BaseOptimizer
from optimizer.ILP.relaxedOptimizer import RelaxedOptimizer
from optimizer.ILP.symmetryBaseOptimizer import SymmetryBaseOptimizer
from optimizer.ILP.symmetryRelaxedOptimizer import SymmetryRelaxedOptimizer
from optimizer.heuristic.slackBasedHeuristic import SlackBasedHeuristic
from data.Environments.default import env as default_env
from data.Environments.relaxed import env as relaxed_env
from data.Environments.symmetry_default import env as symmetry_base_env
from data.Environments.symmetry_relaxed import env as symmetry_relaxed_env

import sys
import igraph
import time

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Please specify optimizer type, task set file (including path), and path to results directory!")
        sys.exit(1)

    optimizer_type = sys.argv[1]
    input_filename = sys.argv[2]
    output_path = sys.argv[3]

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

    elif optimizer_type == "SlackHeuristic":
        optimizer = SlackBasedHeuristic(task_graph, relaxed_env["compute_resources"],
                                             relaxed_env["network"],
                                             relaxed_env["execution_time_multipliers"],
                                             relaxed_env["power"])

    else:
        optimizer = BaseOptimizer(task_graph, default_env["compute_resources"], default_env["network"],
                                  default_env["execution_time_multipliers"], default_env["power"])

    optimizer.compute_deadline()

    start_time = time.process_time()
    optimizer.optimize()
    end_time = time.process_time()

    print("Optimization (" + optimizer_type + ") Time: " + str(end_time - start_time))

    time_dict = {"Time": [end_time - start_time]}
    time_df = pd.DataFrame(time_dict)

    time_df.to_csv(output_path + "/time.csv")

    optimizer.generate_result(output_path)

    if optimizer_type == "SymmetryBase" or optimizer_type == "SymmetryRelaxed":
        optimizer.data_completer(output_path)
