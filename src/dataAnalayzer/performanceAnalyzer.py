import pandas as pd
import sys

TASK_SETS_INSTANCES = 5
CLOUD_BASE_POWER = 62.7007
# ENV_SIZES = ["Medium", "Small"]
ENV_SIZES = ["Large"]
DEADLINES = ["Tight", "Moderate", "Loose"]
# METHODS = ["Strict", "Relaxed", "StrictHeuristic", "RelaxedHeuristic"]
METHODS = ["StrictHeuristic", "RelaxedHeuristic"]
RANDOM_DAGS_GRAPH_SIZES = ["small", "medium", "large"]
DATA_SETS = [
#     {
#         "name": "RandomDAG",
#         "folder": "RandomDAG",
#         "file_pattern": "RandomDAG",
#         "has_graph_size": True
#     },
#     {
#         "name": "RandomChain",
#         "folder": "Random",
#         "file_pattern": "RandomChain",
#         "has_graph_size": False
#     },
#     {
#         "name": "RandomIndependent",
#         "folder": "Random",
#         "file_pattern": "RandomIndependent",
#         "has_graph_size": False
#     }
# ,
    {
        "name": "RandomLargeGraph",
        "folder": "",
        "file_pattern": "R",
        "has_graph_size": False
    }
]

DEADLINE_COEF = {
    "Tight": 1,
    "Moderate": 1.5,
    "Loose": 2,
}


def get_intersection_of_results(df, env_size, deadline, dataset, graph_size):
    data = df.loc[
        df["Env"] == env_size
        ].loc[
        df["DataSet"] == dataset
        ].loc[
        df["GraphSize"] == graph_size
        ].loc[
        df["Deadline"] == deadline
        ]

    ignored = []

    intersection = [x for x in range(TASK_SETS_INSTANCES)]
    for mt in METHODS:
        result = data.loc[
            df["Method"] == mt,
        ]

        res = result["SuccessIndexes"].apply(lambda x: list(map(int, x.split(','))) if x else []).values[0]
        # res = res + result["TimeoutIndexes"].apply(lambda x: list(map(int, x.split(','))) if x else []).values[0]

        if len(res) > 0:
            intersection = list(set(res) & set(intersection))
        else:
            ignored.append(mt)

    return {
        "valid_indexes": intersection,
        "ignored_methods": ignored
    }


def calculate_average_result(path, env_size, deadline, method, dataset_folder, graph_size, folder_name_pattern, valid_indexes):
    result = {
        "time": 0.0,
        "valid_indexes": valid_indexes,
        "base_power": 0.0,
        "communication": 0.0,
        "computation": 0.0,
        "overall": 0.0,
        "avg_power": 0.0,
        "avg_deadline": 0.0
    }
    data_path = path + "/" + env_size + "Arch/" + deadline + "Deadline/" + method + "/" + dataset_folder + "/"
    data_path = data_path + graph_size + "Graph/" if graph_size != "Unknown" else data_path

    for i in range(0, TASK_SETS_INSTANCES):
        instance_path = data_path + folder_name_pattern + str(i) + "/"
        df_time = pd.read_csv(instance_path + "/time.csv")
        result["time"] += df_time.iloc[0]["Time"]
        result["avg_deadline"] += df_time.iloc[0]["deadline"]
        if i in valid_indexes:
            df_energy = pd.read_csv(instance_path + "/consumed_energy.csv")
            result["base_power"] += df_energy.iloc[0]["Base Power"]
            result["communication"] += df_energy.iloc[0]["Communication"]
            result["computation"] += df_energy.iloc[0]["Computation"]
            result["overall"] += df_energy.iloc[0]["Overall"]

    result["time"] /= TASK_SETS_INSTANCES
    result["avg_deadline"] /= TASK_SETS_INSTANCES
    if len(valid_indexes) > 0:
        result["base_power"] /= len(valid_indexes)
        result["communication"] /= len(valid_indexes)
        result["computation"] /= len(valid_indexes)
        result["overall"] /= len(valid_indexes)
        result["avg_power"] = result["overall"] / result["avg_deadline"]

    return result


def write_average_results(path, env_size, deadline, method, data_set, graph_size, result):
    data_path = path + "/" + env_size + "Arch/" + deadline + "Deadline/" + method + "/" + data_set["folder"] + "/"
    data_path = data_path + graph_size + "Graph/" if graph_size != "Unknown" else data_path

    df_energy = pd.DataFrame(columns=["Base Power", "Communication", "Computation", "Overall", "AvgPower"])
    df_time = pd.DataFrame(columns=["Time", "AvgDeadline"])

    df_energy.loc[len(df_energy)] = [result["base_power"], result["communication"], result["computation"],
                                     result["overall"], result["avg_power"]]
    df_time.loc[len(df_time)] = [result["time"], result["avg_deadline"]]

    df_energy.to_csv(data_path + data_set["file_pattern"] + "_average_consumed_energy.csv")
    df_time.to_csv(data_path + data_set["file_pattern"] + "_average_time.csv")


def evaluate_method_performance(path, env_size, deadline, method, dataset_folder, graph_size, folder_name_pattern):
    result = {
        "success": 0,
        "infeasible": 0,
        "timeout": 0,
        "timeout_infeasible": 0,
        "error": 0,
        "success_indexes": [],
        "infeasible_indexes": [],
        "timeout_indexes": [],
        "error_indexes": [],
        "timeout_infeasible_indexes": []
    }
    data_path = path + "/" + env_size + "Arch/" + deadline + "Deadline/" + method + "/" + dataset_folder + "/"
    data_path = data_path + graph_size + "Graph/" if graph_size != "Unknown" else data_path

    for i in range(0, TASK_SETS_INSTANCES):
        instance_path = data_path + folder_name_pattern + str(i) + "/"
        df_time = pd.read_csv(instance_path + "/time.csv")
        if "status" in df_time.columns and df_time.iloc[0]["status"] == -8:
            status = "timeout"
        elif "status" in df_time.columns and df_time.iloc[0]["status"] == -1:
            status = "infeasible"
        elif "status" in df_time.columns and df_time.iloc[0]["status"] == 1:
            status = "success"
        elif "status" in df_time.columns and df_time.iloc[0]["status"] == -9:
            status = "timeout_infeasible"
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
                 "TimeoutInfeasible", "SuccessIndexes", "InfeasibleIndexes", "TimeoutIndexes", "ErrorIndexes",
                 "TimeoutInfeasibleIndexes"])
    for env_size in ENV_SIZES:
        for deadline in DEADLINES:
            for method in METHODS:
                for data_set in DATA_SETS:
                    graph_sizes = ["Unknown"]
                    if data_set["has_graph_size"]:
                        graph_sizes = RANDOM_DAGS_GRAPH_SIZES

                    for graph_size in graph_sizes:
                        res = evaluate_method_performance(root_folder_path, env_size, deadline, method,
                                                          data_set["folder"], graph_size, data_set["file_pattern"])
                        df.loc[len(df)] = [env_size, deadline, method, data_set["name"], graph_size, res["success"],
                                           res["infeasible"], res["timeout"], res["error"], res["timeout_infeasible"],
                                           ",".join(map(str, res["success_indexes"])),
                                           ",".join(map(str, res["infeasible_indexes"])),
                                           ",".join(map(str, res["timeout_indexes"])),
                                           ",".join(map(str, res["error_indexes"])),
                                           ",".join(map(str, res["timeout_infeasible_indexes"]))]

    df.to_csv(root_folder_path + "/performance.csv")

    # df_deadlines = pd.read_csv(root_folder_path + "/Deadlines.csv")

    for env_size in ENV_SIZES:
        for deadline in DEADLINES:
            for data_set in DATA_SETS:
                graph_sizes = ["Unknown"]
                if data_set["has_graph_size"]:
                    graph_sizes = RANDOM_DAGS_GRAPH_SIZES

                for graph_size in graph_sizes:
                    intersection = get_intersection_of_results(df, env_size, deadline, data_set["name"], graph_size)
                    for method in METHODS:
                        valid_indexes = intersection["valid_indexes"]
                        if method in intersection["ignored_methods"]:
                            valid_indexes = []

                        # avg_tight_deadline = df_deadlines.loc[df_deadlines["DataSet"] == data_set["name"]].loc[
                        #     df_deadlines["Env"] == env_size].loc[df_deadlines["GraphSize"] == graph_size][
                        #     "Avg_Tight"].values[0]

                        result = calculate_average_result(root_folder_path, env_size, deadline, method,
                                                          data_set["folder"],
                                                          graph_size, data_set["file_pattern"], valid_indexes)

                        write_average_results(root_folder_path, env_size, deadline, method, data_set,
                                              graph_size, result)

# ../../output/NewData
