import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

space_positions = {"small": [1, 4], "medium": [1,6]}
size_vars = {"small": {"width": 8, "nodes": 11, "ub_edge": 3}, "medium": {"width": 10, "nodes": 19, "ub_edge": 5}}


def node_detail(data, label, type, color, env_size):
    nodes = np.arange(0, size_vars[env_size]["nodes"])
    data_arr = []
    temp = data[type].tolist()
    i = 0
    j = 0
    while i < len(temp) + len(space_positions[env_size]):
        if i in space_positions[env_size]:
            data_arr.append(0)
        else:
            data_arr.append(temp[j])
            j += 1
        i += 1

    plt.figure(figsize=(size_vars[env_size]["width"], 6))
    plt.bar(nodes, data_arr, width=0.4, label=label, align='center', alpha=0.7, color=color)
    x_labels = ['Cloud'] + [' '] + [f'L{i}' for i in range(1, size_vars[env_size]["ub_edge"])] + [' '] + [f'D{i}' for i in range(size_vars[env_size]["ub_edge"], size_vars[env_size]["nodes"] - 2)]
    plt.xticks(range(size_vars[env_size]["nodes"]), x_labels)
    plt.xlabel('Node')
    plt.ylabel('Energy')
    plt.legend()
    # plt.savefig(OUTPUT_PATH + '/charts/' + deadline + "Deadline/" + env_size + "/" + label + '_' + type + '_node_energy_comparison.svg', format="svg",
    #             bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/' + deadline + "Deadline/" + env_size + "/" + label + '_' + type + '_node_energy_comparison.png', format="png",
                bbox_inches='tight')
    plt.close()


def overall_result(data, labels, colors, output_file_name):
    methods = np.arange(0, len(data))
    plt.figure(figsize=(6, 6))
    bars = plt.bar(methods, data, width=0.3, align='center', alpha=0.7, color=colors)

    for bar, value in zip(bars, data):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(value, 2), ha='center', va='bottom', fontsize=12)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=14)
    # plt.xlabel('Methods')
    plt.ylabel('Overall Energy', fontsize=14)
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_overall_node_energy_comparison.svg', format="svg",
    #             bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_overall_node_energy_comparison.png', format="png",
                bbox_inches='tight')
    plt.close()


def time_plot(data, labels, colors, output_file_name):
    methods = np.arange(0, len(data))
    plt.figure(figsize=(6, 6))
    bars = plt.bar(methods, data, width=0.3, align='center', alpha=0.7, color=colors)

    for bar, value in zip(bars, data):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(value, 2), ha='center', va='bottom', fontsize=12)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=14)
    # plt.xlabel('Methods')
    plt.ylabel('Optimization Time', fontsize=14)
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_time_comparison.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_time_comparison.png', format="png", bbox_inches='tight')
    plt.close()


def success_plot(data, labels, colors, output_file_name):
    methods = np.arange(0, len(data))
    plt.figure(figsize=(6, 6))
    bars = plt.bar(methods, data, width=0.3, align='center', alpha=0.7, color=colors)

    for bar, value in zip(bars, data):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(round(value, 2)) + "%", ha='center', va='bottom', fontsize=12)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=14)
    # plt.xlabel('Methods')
    plt.ylabel('Success Rate', fontsize=14)
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_success_rate.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_success_rate.png', format="png", bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please specify output directory!")
        sys.exit(1)

    OUTPUT_PATH = sys.argv[1]

    env_sizes = ["small", "medium"]
    # env_sizes = ["small"]
    # deadlines = ["Short", "Medium", "Long"]
    deadlines = ["Long"]
    random_tasks = ["RandomChain", "RandomFullyParallel"]

    for deadline in deadlines:
        for env_size in env_sizes:
            node_base = pd.read_csv(OUTPUT_PATH + '/Base/' + deadline + 'Deadline/T4/' + env_size + '/nodes_energy.csv')
            node_relaxed = pd.read_csv(OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/T4/' + env_size + '/nodes_energy.csv')
            node_base_heuristic = pd.read_csv(OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/nodes_energy.csv')
            node_relaxed_heuristic = pd.read_csv(OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/nodes_energy.csv')

            node_detail(node_base, 'ILP-Base', 'Overall', 'blue', env_size)
            node_detail(node_relaxed, 'ILP-Relaxed', 'Overall', 'green', env_size)
            node_detail(node_base_heuristic, 'Heuristic-Base', 'Overall', 'lightseagreen', env_size)
            node_detail(node_relaxed_heuristic, 'Heuristic-Relaxed', 'Overall', 'springgreen', env_size)

            # Overall Energy
            overall_base = pd.read_csv(OUTPUT_PATH + '/Base/' + deadline + 'Deadline/T4/' + env_size + '/consumed_energy.csv')
            overall_relaxed = pd.read_csv(OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/T4/' + env_size + '/consumed_energy.csv')
            overall_base_heuristic = pd.read_csv(OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/consumed_energy.csv')
            overall_relaxed_heuristic = pd.read_csv(OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/consumed_energy.csv')

            overall_energy_consumptions = [
                overall_base.iloc[0]["Overall"],
                overall_relaxed.iloc[0]["Overall"],
                overall_base_heuristic.iloc[0]["Overall"],
                overall_relaxed_heuristic.iloc[0]["Overall"],
            ]

            overall_result(overall_energy_consumptions,
                           ["ILP\nBase", "ILP\nRelaxed", "Heuristic\nBase", "Heuristic\nRelaxed"],
                           ["blue", "green", "lightseagreen", "springgreen"], deadline + "Deadline/" + env_size + "/SDE")



            # Optimization Time
            time_base = pd.read_csv(OUTPUT_PATH + '/Base/' + deadline + 'Deadline/T4/' + env_size + '/time.csv')
            time_relaxed = pd.read_csv(OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/T4/' + env_size + '/time.csv')
            time_base_heuristic = pd.read_csv(OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/time.csv')
            time_relaxed_heuristic = pd.read_csv(OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/time.csv')

            times = [
                time_base.iloc[0]["Time"],
                time_relaxed.iloc[0]["Time"],
                time_base_heuristic.iloc[0]["Time"],
                time_relaxed_heuristic.iloc[0]["Time"],
            ]
            time_plot(times,
                      ["ILP\nBase", "ILP\nRelaxed", "Heuristic\nBase", "Heuristic\nRelaxed"],
                      ["blue", "green", "lightseagreen", "springgreen"], deadline + "Deadline/" + env_size + "/SDETimePlot")

            rate = [
                100,
                100,
                100,
                100
            ]

            success_plot(rate, ["ILP\nBase", "ILP\nRelaxed", "Heuristic\nBase", "Heuristic\nRelaxed"],
                      ["blue", "green", "lightseagreen", "springgreen"], deadline + "Deadline/" + env_size + "/SDESuccessRate")

            for random_task in random_tasks:
                overall_random_base = pd.read_csv(
                    OUTPUT_PATH + '/Base/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_consumed_energy.csv')
                overall_random_relaxed = pd.read_csv(
                    OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_consumed_energy.csv')
                overall_random_base_heuristic = pd.read_csv(
                    OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_consumed_energy.csv')
                overall_random_relaxed_heuristic = pd.read_csv(
                    OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_consumed_energy.csv')

                overall_random_energy_consumptions = [
                    overall_random_base.iloc[0]["Overall"],
                    overall_random_relaxed.iloc[0]["Overall"],
                    overall_random_base_heuristic.iloc[0]["Overall"],
                    overall_random_relaxed_heuristic.iloc[0]["Overall"],
                ]
                overall_result(overall_random_energy_consumptions,
                               ["ILP\nBase", "ILP\nRelaxed", "Heuristic\nBase", "Heuristic\nRelaxed"],
                               ["blue", "green", "lightseagreen", "springgreen"],
                               deadline + "Deadline/" + env_size + "/" + random_task)

                time_random_base = pd.read_csv(OUTPUT_PATH + '/Base/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_time.csv')
                time_random_relaxed = pd.read_csv(OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_time.csv')
                time_random_base_heuristic = pd.read_csv(OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_time.csv')
                time_random_relaxed_heuristic = pd.read_csv(OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_time.csv')
                random_times = [
                    time_random_base.iloc[0]["Time"],
                    time_random_relaxed.iloc[0]["Time"],
                    time_random_base_heuristic.iloc[0]["Time"],
                    time_random_relaxed_heuristic.iloc[0]["Time"],
                ]

                time_plot(random_times,
                          ["ILP\nBase", "ILP\nRelaxed", "Heuristic\nBase", "Heuristic\nRelaxed"],
                          ["blue", "green", "lightseagreen", "springgreen"], deadline + "Deadline/" + env_size + "/" + random_task)

                random_rate = [
                    round(((30 - time_random_base.iloc[0]["infeasible"]) / 30) * 100),
                    round(((30 - time_random_relaxed.iloc[0]["infeasible"]) / 30) * 100),
                    round(((30 - time_random_base_heuristic.iloc[0]["infeasible"]) / 30) * 100),
                    round(((30 - time_random_relaxed_heuristic.iloc[0]["infeasible"]) / 30) * 100),
                ]

                success_plot(random_rate, ["ILP\nBase", "ILP\nRelaxed", "Heuristic\nBase", "Heuristic\nRelaxed"],
                             ["blue", "green", "lightseagreen", "springgreen"],
                             deadline + "Deadline/" + env_size + "/" + random_task + "SuccessRate")




