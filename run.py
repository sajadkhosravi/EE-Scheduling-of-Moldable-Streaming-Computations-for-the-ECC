import subprocess
import pandas as pd

def optimization(model_type, input_path, output_path, env_size, lb, ub, graph_type, inp_temp):
    for i in range(lb, ub):
        subprocess.run("mkdir ./output/" + model_type + "/Random/" + env_size + "/" + graph_type + str(i), shell=True, check=True)
        command_template = "python ./src/main.py " + model_type + " " + env_size + " " + input_path + inp_temp + str(i) + ".graphml " + output_path + graph_type + str(i)
        try:
            # Execute the command using subprocess
            subprocess.run(command_template, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")

    print("Commands executed successfully.")


known_graph_tasks = [
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "small",
        "input_temp": "chain_5_tasks_6_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "small",
        "input_temp": "fully_parallel_5_tasks_6_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "medium",
        "input_temp": "chain_5_tasks_12_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_small_data_",
        "lb": 0,
        "ub": 10,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_medium_data_",
        "lb": 10,
        "ub": 20,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomFullyParallel",
        "env_size": "medium",
        "input_temp": "fully_parallel_5_tasks_12_task_sets_random_graph_large_data_",
        "lb": 20,
        "ub": 30,
        "method_types": ["Relaxed"]
    },
]

random_graph_tasks = [
    {
        "graph_type": "RandomDAG",
        "env_size": "small",
        "input_temp": "graph_ts6_task_sets_",
        "lb": 0,
        "ub": 30,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomDAG",
        "env_size": "small",
        "input_temp": "graph_ts6_task_sets_",
        "lb": 0,
        "ub": 30,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomDAG",
        "env_size": "small",
        "input_temp": "graph_ts6_task_sets_",
        "lb": 0,
        "ub": 30,
        "method_types": ["Relaxed"]
    },
    {
        "graph_type": "RandomDAG",
        "env_size": "medium",
        "input_temp": "graph_ts12_task_sets_",
        "lb": 0,
        "ub": 30,
        "method_types": ["Base"]
    },
    {
        "graph_type": "RandomDAG",
        "env_size": "medium",
        "input_temp": "graph_ts12_task_sets_",
        "lb": 0,
        "ub": 30,
        "method_types": ["BaseHeuristic", "RelaxedHeuristic"]
    },
    {
        "graph_type": "RandomDAG",
        "env_size": "medium",
        "input_temp": "graph_ts12_task_sets_",
        "lb": 0,
        "ub": 30,
        "method_types": ["Relaxed"]
    }
]


# for task in known_graph_tasks:
#     for mt in task["method_types"]:
#         input_dir = "./data/Workflows/NewTasks/" + task["graph_type"] + "/"
#         optimization(mt, input_dir, task["env_size"], task["lb"], task["ub"], task["graph_type"], task["input_temp"])

graph_sizes = ["small", "medium", "large"]

for graph_size in graph_sizes:
    for task in random_graph_tasks:
        for mt in task["method_types"]:
            input_dir = "./data/Workflows/NewTasks/RandomGraphs/" + graph_size + "Graph/"
            output_dir = "./output/" + mt + "/Random/" + graph_size + "Graph/" + task["env_size"] + "/"
            optimization(mt, input_dir, output_dir, task["env_size"], task["lb"], task["ub"], task["graph_type"], task["input_temp"])