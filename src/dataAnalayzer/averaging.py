import pandas as pd

task_sets_number = 30
methods = ["Base", "BaseHeuristic", "Relaxed", "RelaxedHeuristic"]
task_types = ["Chain", "Independent"]
env_sizes = ["small", "medium"]
deadlines = ["Tight", "Moderate", "Loose"]
random_graph_sizes = ["large", "medium", "small"]

infeasible_solutions = pd.DataFrame(columns=["Approach", "Task", "Count"])
for deadline in deadlines:
    for env_size in env_sizes:
        for type_name in methods:
            for task_type in task_types:
                no_feasible_solution_count = 0
                timeout_count = 0
                total_values = {
                    "Base Power": 0,
                    "Communication": 0,
                    "Computation": 0,
                    "Overall": 0,
                    "Time": 0.0
                }
                for i in range(0, task_sets_number):
                    not_feasible = False
                    df = pd.DataFrame()
                    time_file_name = "../../output/"+type_name + "/" + deadline + "Deadline/Random/"+env_size+"/Random" + task_type + str(i) + "/time.csv"
                    df_time = pd.read_csv(time_file_name)
                    try:
                        file_name = "../../output/"+ type_name + "/" + deadline + "Deadline/Random/"+env_size+"/Random" + task_type + str(i) + "/consumed_energy.csv"
                        # time_file_name = "../../output/"+type_name + "/" + deadline + "Deadline/Random/"+env_size+"/Random" + task_type + str(i) + "/time.csv"
                        active_node_file_name = "../../output/"+type_name + "/" + deadline + "Deadline/Random/"+env_size+"/Random" + task_type + str(i) + "/active_nodes.csv"

                        df = pd.read_csv(file_name)
                        # df_time = pd.read_csv(time_file_name)
                        pd.read_csv(active_node_file_name)
                    except Exception as e:
                        if "status" in df_time.columns and df_time.iloc[0]["status"] == -9:
                            timeout_count += 1
                            continue
                        else:
                            no_feasible_solution_count += 1
                            not_feasible = True


                    if not not_feasible:
                        total_values["Base Power"] += df.loc[0, "Base Power"]
                        total_values["Communication"] += df.loc[0, "Communication"]
                        total_values["Computation"] += df.loc[0, "Computation"]
                        total_values["Overall"] += df.loc[0, "Overall"]

                    total_values["Time"] += df_time.loc[0, "Time"]

                if (task_sets_number - no_feasible_solution_count - timeout_count) > 0:
                    total_values["Base Power"] = total_values["Base Power"] / (task_sets_number - no_feasible_solution_count - timeout_count)
                    total_values["Communication"] = total_values["Communication"] / (task_sets_number - no_feasible_solution_count - timeout_count)
                    total_values["Computation"] = total_values["Computation"] / (task_sets_number - no_feasible_solution_count - timeout_count)
                    total_values["Overall"] = total_values["Overall"] / (task_sets_number - no_feasible_solution_count - timeout_count)
                    total_values["Time"] = total_values["Time"] / (task_sets_number - timeout_count)
                    total_values["infeasible"] = no_feasible_solution_count
                    total_values["timeout"] = timeout_count
                else:
                    total_values["Base Power"] = 0.0
                    total_values["Communication"] = 0.0
                    total_values["Computation"] = 0.0
                    total_values["Overall"] = 0.0
                    if task_sets_number - timeout_count > 0:
                        total_values["Time"] = total_values["Time"] / (task_sets_number - timeout_count)
                    else:
                        total_values["Time"] = 0.0
                    total_values["infeasible"] = no_feasible_solution_count


                df = pd.DataFrame(columns=["Base Power", "Communication", "Computation", "Overall"])
                df.loc[0] = total_values

                df.to_csv("../../output/" + type_name + "/" + deadline + "Deadline/Random/"+env_size+"/Random"+task_type+"_consumed_energy.csv")

                df = pd.DataFrame(columns=["Time", "infeasible", "timeout"])
                df.loc[0] = total_values

                df.to_csv("../../output/"+type_name+ "/" + deadline + "Deadline/Random/"+env_size+"/Random"+task_type+"_time.csv")

                print(str(no_feasible_solution_count) + " of test cases of " + task_type +" with env size " + env_size + " don't have any feasible solution by " + type_name + " approach with a " + deadline + " deadline")


    print("----------------------------------------------")

task_sets_number = 30
for method in methods:
    for deadline in deadlines:
        for size in random_graph_sizes:
            for env_size in env_sizes:
                no_feasible_solution_count = 0
                timeout_count = 0
                total_values = {
                    "Base Power": 0,
                    "Communication": 0,
                    "Computation": 0,
                    "Overall": 0,
                    "Time": 0.0
                }
                for i in range(0, task_sets_number):
                    not_feasible = False
                    df = pd.DataFrame()
                    time_file_name = "../../output/RandomDAG/" + method + "/" + deadline + "/Random/" + size + "Graph/" + env_size + "/RandomDAG" + str(
                        i) + "/time.csv"
                    df_time = pd.read_csv(time_file_name)
                    try:
                        file_name = "../../output/RandomDAG/" + method + "/" + deadline + "/Random/" + size + "Graph/" + env_size + "/RandomDAG" + str(
                            i) + "/consumed_energy.csv"

                        active_node_file_name = "../../output/RandomDAG/" + method + "/" + deadline + "/Random/" + size + "Graph/" + env_size + "/RandomDAG" + str(
                            i) + "/active_nodes.csv"

                        df = pd.read_csv(file_name)
                        pd.read_csv(active_node_file_name)
                    except Exception as e:
                        if df_time.iloc[0]["status"] == -9:
                            timeout_count += 1
                            continue
                        else:
                            no_feasible_solution_count += 1
                            not_feasible = True

                    if not not_feasible:
                        total_values["Base Power"] += df.loc[0, "Base Power"]
                        total_values["Communication"] += df.loc[0, "Communication"]
                        total_values["Computation"] += df.loc[0, "Computation"]
                        total_values["Overall"] += df.loc[0, "Overall"]

                    total_values["Time"] += df_time.loc[0, "Time"]

                if (task_sets_number - no_feasible_solution_count - timeout_count) > 0:
                    total_values["Base Power"] = total_values["Base Power"] / (
                                task_sets_number - no_feasible_solution_count - timeout_count)
                    total_values["Communication"] = total_values["Communication"] / (
                                task_sets_number - no_feasible_solution_count - timeout_count)
                    total_values["Computation"] = total_values["Computation"] / (
                                task_sets_number - no_feasible_solution_count - timeout_count)
                    total_values["Overall"] = total_values["Overall"] / (task_sets_number - no_feasible_solution_count - timeout_count)
                    total_values["Time"] = total_values["Time"] / (task_sets_number - timeout_count)
                    total_values["infeasible"] = no_feasible_solution_count
                    total_values["timeout"] = timeout_count
                else:
                    total_values["Base Power"] = 0.0
                    total_values["Communication"] = 0.0
                    total_values["Computation"] = 0.0
                    total_values["Overall"] = 0.0
                    if task_sets_number - timeout_count > 0:
                        total_values["Time"] = total_values["Time"] / (task_sets_number - timeout_count)
                    else:
                        total_values["Time"] = 0.0
                    total_values["infeasible"] = no_feasible_solution_count
                    total_values["timeout"] = timeout_count

                df = pd.DataFrame(columns=["Base Power", "Communication", "Computation", "Overall"])
                df.loc[0] = total_values

                df.to_csv("../../output/RandomDAG/" + method + "/" + deadline + "/Random/" + size + "Graph/" + env_size + "/Average_consumed_energy.csv")

                df = pd.DataFrame(columns=["Time", "infeasible", "timeout"])
                df.loc[0] = total_values

                df.to_csv(
                    "../../output/RandomDAG/" + method + "/" + deadline + "/Random/" + size + "Graph/" + env_size + "/Average_time.csv")

                print("Method: " + method)
                print("Deadline: " + deadline)
                print("Graph: " + size)
                print("Env_size: " + env_size)
                print("no_feasible_solution_count: " + str(no_feasible_solution_count))
                print("timeout: " + str(timeout_count))
                print("--------------------------------------------------------------")
