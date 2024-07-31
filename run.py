import subprocess

def optimization(method, input_path, output_path, env_size, lb, ub, graph_type, inp_temp):
    for i in range(lb, ub):
        subprocess.run("mkdir " + output_path + graph_type + str(i), shell=True, check=True)
        command_template = "python ./src/main.py " + method + " " + env_size + " " + input_path + inp_temp + str(i) + ".graphml " + output_path + graph_type + str(i)
        try:
            # Execute the command using subprocess
            subprocess.run(command_template, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {e}")

    print("Commands executed successfully.")


known_graph_tasks = [
    {
        "graph_type": "RandomChain",
        "env_size": "Small",
        "input_temp": "graph_ts6_task_sets_",
        "lb": 0,
        "ub": 20,
        "method_types": ["Strict", "StrictHeuristic", "RelaxedHeuristic", "Relaxed"]
    },
    {
        "graph_type": "RandomIndependent",
        "env_size": "Small",
        "input_temp": "graph_ts6_task_sets_",
        "lb": 0,
        "ub": 20,
        "method_types": ["Strict", "StrictHeuristic", "RelaxedHeuristic", "Relaxed"]
    },
    {
        "graph_type": "RandomChain",
        "env_size": "Medium",
        "input_temp": "graph_ts12_task_sets_",
        "lb": 0,
        "ub": 20,
        "method_types": ["Strict", "StrictHeuristic", "RelaxedHeuristic", "Relaxed"]
    },
    {
        "graph_type": "RandomIndependent",
        "env_size": "Medium",
        "input_temp": "graph_ts12_task_sets_",
        "lb": 0,
        "ub": 20,
        "method_types": ["Strict", "StrictHeuristic", "RelaxedHeuristic", "Relaxed"]
    }
]

random_graph_tasks = [
    {
        "graph_type": "RandomDAG",
        "env_size": "Small",
        "input_temp": "graph_ts6_task_sets_",
        "lb": 0,
        "ub": 20,
        "method_types": ["Strict", "StrictHeuristic", "RelaxedHeuristic", "Relaxed"]
    },
    {
        "graph_type": "RandomDAG",
        "env_size": "Medium",
        "input_temp": "graph_ts12_task_sets_",
        "lb": 0,
        "ub": 20,
        "method_types": ["Strict", "StrictHeuristic", "RelaxedHeuristic", "Relaxed"]
    }
]


for task in known_graph_tasks:
    for mt in task["method_types"]:
        input_dir = "./data/Workflows/" + task["graph_type"] + "/"
        output_dir = "./output/" + task["env_size"] + "Arch/TightDeadline/" + mt + "/Random/"
        optimization(mt, input_dir, output_dir, task["env_size"], task["lb"], task["ub"], task["graph_type"], task["input_temp"])

graph_sizes = ["small", "medium", "large"]

for graph_size in graph_sizes:
    for task in random_graph_tasks:
        for mt in task["method_types"]:
            input_dir = ("./data/Workflows/RandomGraphs/") + graph_size + "Graph/"
            output_dir = "./output/" + task["env_size"] + "Arch/LooseDeadline/" + mt + "/RandomDAG/" + graph_size + "Graph/"
            optimization(mt, input_dir, output_dir, task["env_size"], task["lb"], task["ub"], task["graph_type"], task["input_temp"])