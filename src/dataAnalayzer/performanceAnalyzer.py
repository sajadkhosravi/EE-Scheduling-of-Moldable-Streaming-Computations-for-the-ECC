import pandas as pd
import sys

TASK_SETS_INSTANCES = 50
ENV_SIZES = ["Medium", "Small"]
DEADLINES = ["Tight", "Moderate", "Loose"]
METHODS = ["StrictHeuristic", "RelaxedHeuristic"]
RANDOM_DAGS_GRAPH_SIZES = ["small", "medium", "large"]
DATA_SETS = [
    {
        "name": "RandomDAG",
        "file_pattern": "RandomDAG",
        "has_graph_size": True
    }
]


def evaluate_method_performance(path, env_size, deadline, method, dataset, graph_size, file_name_pattern):
    result = {
        "success": 0,
        "infeasible": 0,
        "timeout": 0,
        "error": 0,
        "success_indexes": [],
        "infeasible_indexes": [],
        "timeout_indexes": [],
        "error_indexes": []
    }
    data_path = path + "/" + env_size + "Arch/" + deadline + "Deadline/" + method + "/" + dataset + "/"
    data_path = data_path + graph_size + "Graph/" if graph_size != "Unknown" else data_path

    for i in range(0, TASK_SETS_INSTANCES):
        instance_path = data_path + file_name_pattern + str(i) + "/"
        df_time = pd.read_csv(instance_path + "/time.csv")
        if "status" in df_time.columns and df_time.iloc[0]["status"] == -9:
            status = "timeout"
        elif "status" in df_time.columns and df_time.iloc[0]["status"] == -1:
            status = "infeasible"
        elif "status" in df_time.columns and df_time.iloc[0]["status"] == 1:
            status = "success"
        else:
            status = "error"

        result[status] += 1
        result[status + "_indexes"].append(i)

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please specify data path!")
        sys.exit(1)

    root_folder_path = sys.argv[1]

    df = pd.DataFrame(
        columns=["Env", "Deadline", "Method", "DataSet", "GraphSize", "Success", "Infeasible", "Timeout", "Error",
                 "SuccessIndexes", "InfeasibleIndexes", "TimeoutIndexes", "ErrorIndexes"])
    for env_size in ENV_SIZES:
        for deadline in DEADLINES:
            for method in METHODS:
                for data_set in DATA_SETS:
                    graph_sizes = ["Unknown"]
                    if data_set["has_graph_size"]:
                        graph_sizes = RANDOM_DAGS_GRAPH_SIZES

                    for graph_size in graph_sizes:
                        res = evaluate_method_performance(root_folder_path, env_size, deadline, method,
                                                          data_set["name"], graph_size, data_set["file_pattern"])
                        df.loc[len(df)] = [env_size, deadline, method, data_set["name"], graph_size, res["success"],
                                           res["infeasible"], res["timeout"], res["error"],
                                           ",".join(map(str, res["success_indexes"])),
                                           ",".join(map(str, res["infeasible_indexes"])),
                                           ",".join(map(str, res["timeout_indexes"])),
                                           ",".join(map(str, res["error_indexes"]))]

    df.to_csv(root_folder_path + "/performance.csv")

# ../../output/NewData