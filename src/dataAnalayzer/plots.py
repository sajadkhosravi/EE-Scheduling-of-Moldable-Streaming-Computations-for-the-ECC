import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import sys
import math

space_positions = {"small": [1, 4], "medium": [1, 6]}
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

    plt.figure(figsize=(10, 6))
    plt.bar(nodes, data_arr, width=0.4, label=label, align='center', alpha=0.7, color=color)
    x_labels = ['Cloud'] + [' '] + [f'L{i}' for i in range(1, size_vars[env_size]["ub_edge"])] + [' '] + [f'D{i}' for i
                                                                                                          in range(
            size_vars[env_size]["ub_edge"], size_vars[env_size]["nodes"] - 2)]
    plt.xticks(range(size_vars[env_size]["nodes"]), x_labels, fontsize=30, rotation=90)
    plt.xlabel('Node', fontsize=30)
    plt.ylabel('Energy', fontsize=30)
    plt.yticks(fontsize=30)
    # plt.legend()
    # plt.savefig(OUTPUT_PATH + '/charts/' + deadline + "Deadline/" + env_size + "/" + label + '_' + type + '_node_energy_comparison.svg', format="svg",
    #             bbox_inches='tight')
    plt.savefig(
        OUTPUT_PATH + '/charts/' + deadline + "Deadline/" + env_size + "/" + label + '_' + type + '_node_energy_comparison.png',
        format="png",
        bbox_inches='tight')
    plt.close()


def plot_merged(data, x_labels, y_label, legend_labels, colors, output_file_name):
    num_deadlines = len(data)
    num_values = len(data[0])

    max_value = np.max(data)
    deadlines = np.arange(0, num_deadlines)

    plt.figure(figsize=(10, 6))

    bar_width = 0.2
    bar_offsets = np.linspace(-bar_width * (num_values - 1) / 2, bar_width * (num_values - 1) / 2, num_values)

    for i in range(num_values):
        bars = plt.bar(deadlines + bar_offsets[i], [row[i] for row in data], width=bar_width, align='center',
                       alpha=0.7, color=colors[i], label=legend_labels[i])

        for bar, value in zip(bars, [row[i] for row in data]):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), " " + str(round(value, 2)),
                     ha='center', va='bottom', fontsize=28, rotation=90)

    plt.xticks(range(num_deadlines), x_labels, fontsize=30)
    plt.ylabel(y_label, fontsize=30)
    plt.yticks(fontsize=28)
    plt.ylim(0, max_value * 1.5)
    plt.legend(fontsize=20, loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)

    plt.savefig(output_file_name, format="png", bbox_inches='tight')
    plt.close()


def rates_plot_merged(data, x_labels, y_label, legend_labels, colors, output_file_name):
    num_values = len(data[0])

    deadlines = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bar_width = 0.2
    bar_offsets = np.linspace(-bar_width * (num_values - 1) / 2, bar_width * (num_values - 1) / 2, num_values)

    for i in range(num_values):
        bars = plt.bar(deadlines + bar_offsets[i], [row[i] for row in data], width=bar_width, align='center',
                       alpha=0.7, color=colors[i], label=legend_labels[i])

        for bar, value in zip(bars, [row[i] for row in data]):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), " " + str(round(value, 2)) + "%",
                     ha='center', va='bottom', fontsize=28, rotation=90)

    plt.xticks(range(len(data)), x_labels, fontsize=30)
    # plt.xlabel('Methods')
    plt.ylabel(y_label, fontsize=30)
    plt.yticks(fontsize=28)
    plt.ylim(0, 100)
    plt.legend(fontsize=20, loc='center left', bbox_to_anchor=(1, 0.5), ncol=1)
    plt.savefig(output_file_name, format="png", bbox_inches='tight')
    plt.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please specify output directory!")
        sys.exit(1)

    OUTPUT_PATH = sys.argv[1]

    env_sizes = ["Small", "Medium"]
    deadlines = ["Tight", "Moderate", "Loose"]
    methods = ["Strict", "Relaxed", "StrictHeuristic", "RelaxedHeuristic"]
    task_sets = ["Random", "RandomDAG", "SDE"]
    random_task_sets = ["RandomChain", "RandomIndependent"]
    randomDAG_graph_sizes = ["large", "medium", "small"]

    deadline_df = pd.read_csv(OUTPUT_PATH + '/Deadlines.csv')

    for env_size in env_sizes:
        for task_set in task_sets:
            if task_set == "SDE":
                overall_energy_consumptions = [[], [], []]
                avg_energy_consumptions = [[], [], []]
                times = [[], [], []]

                # Overall Energy
                for deadline_idx in range(len(deadlines)):
                    for method_idx in range(len(methods)):
                        energy_consumption = pd.read_csv(
                            OUTPUT_PATH + '/' + env_size + 'Arch/' + deadlines[deadline_idx] + 'Deadline/' + methods[
                                method_idx] + '/SDE/consumed_energy.csv')
                        overall_energy_consumptions[deadline_idx].append(energy_consumption.iloc[0]["Overall"])
                        makespan = deadline_df.loc[deadline_df["Graph"] == "SDE"].loc[
                            deadline_df["Method"] == methods[method_idx]].loc[deadline_df["EnvSize"] == env_size].iloc[
                            0]["Avg_" + deadlines[deadline_idx]]
                        avg_energy_consumptions[deadline_idx].append(energy_consumption.iloc[0]["Overall"] / makespan)

                        time = pd.read_csv(
                            OUTPUT_PATH + '/' + env_size + 'Arch/' + deadlines[deadline_idx] + 'Deadline/' + methods[
                                method_idx] + '/SDE/time.csv')
                        times[deadline_idx].append(time.iloc[0]["Time"])

                plot_merged(overall_energy_consumptions,
                            ["Tight", "Moderate", "Loose"],
                            'Overall Energy',
                            ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                            ["darkred", "red", "tomato", "orange"],
                            OUTPUT_PATH + '/charts/' + env_size + 'Arch/SDE/overall_energy_comparison.png')

                plot_merged(avg_energy_consumptions,
                            ["Tight", "Moderate", "Loose"],
                            'Average Energy',
                            ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                            ["darkred", "red", "tomato", "orange"],
                            OUTPUT_PATH + '/charts/' + env_size + 'Arch/SDE/average_energy_comparison.png')

                plot_merged(times,
                            ["Tight", "Moderate", "Loose"],
                            'Optimization Time (S)',
                            ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                            ["darkred", "red", "tomato", "orange"],
                            OUTPUT_PATH + '/charts/' + env_size + "Arch/SDE/overall_time_comparison.png")

            elif task_set == "Random":
                for random_task_set in random_task_sets:
                    times = [[], [], []]
                    random_rates = [[], [], []]
                    timeout_rates = [[], [], []]
                    infeasible_rates = [[], [], []]
                    overall_random_energy_consumptions = [[], [], []]
                    avg_random_energy_consumptions = [[], [], []]
                    for deadline_idx in range(len(deadlines)):
                        for method_idx in range(len(methods)):
                            energy_consumption = pd.read_csv(
                                OUTPUT_PATH + '/' + env_size + 'Arch/' + deadlines[deadline_idx] + 'Deadline/' +
                                methods[method_idx] + '/Random/' + random_task_set + '_consumed_energy.csv')
                            overall_random_energy_consumptions[deadline_idx].append(
                                energy_consumption.iloc[0]["Overall"])

                            makespan = deadline_df.loc[deadline_df["Graph"] == random_task_set].loc[
                                deadline_df["Method"] == methods[method_idx]].loc[
                                deadline_df["EnvSize"] == env_size].iloc[
                                0]["Avg_" + deadlines[deadline_idx]]
                            avg_random_energy_consumptions[deadline_idx].append(
                                energy_consumption.iloc[0]["Overall"] / makespan)

                            time = pd.read_csv(
                                OUTPUT_PATH + '/' + env_size + 'Arch/' + deadlines[deadline_idx] + 'Deadline/' +
                                methods[
                                    method_idx] + '/Random/' + random_task_set + '_time.csv')
                            times[deadline_idx].append(time.iloc[0]["Time"])
                            random_rates[deadline_idx].append(
                                round(((30 - time.iloc[0]["infeasible"] - time.iloc[0]["timeout"]) / 30) * 100))
                            timeout_rates[deadline_idx].append(round(((time.iloc[0]["timeout"]) / 30) * 100))
                            infeasible_rates[deadline_idx].append(round(((time.iloc[0]["infeasible"]) / 30) * 100))

                    plot_merged(overall_random_energy_consumptions,
                                ["Tight", "Moderate", "Loose"],
                                'Overall Energy',
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["darkred", "red", "tomato", "orange"],
                                OUTPUT_PATH + '/charts/' + env_size + 'Arch/Random/' + random_task_set + '_overall_energy_comparison.png')

                    plot_merged(avg_random_energy_consumptions,
                                ["Tight", "Moderate", "Loose"],
                                'Average Energy',
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["darkred", "red", "tomato", "orange"],
                                OUTPUT_PATH + '/charts/' + env_size + 'Arch/Random/' + random_task_set + '_average_energy_comparison.png')

                    rates_plot_merged(random_rates,
                                      ["Tight", "Moderate", "Loose"],
                                      'Success Rate',
                                      ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                      ["darkred", "red", "tomato", "orange"],
                                      OUTPUT_PATH + '/charts/' + env_size + "Arch/Random/" + random_task_set + "_success_rate.png")

                    rates_plot_merged(timeout_rates,
                                      ["Tight", "Moderate", "Loose"],
                                      'Timeout Rate',
                                      ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                      ["darkred", "red", "tomato", "orange"],
                                      OUTPUT_PATH + '/charts/' + env_size + "Arch/Random/" + random_task_set + "_timeout_rate.png")

                    rates_plot_merged(infeasible_rates,
                                      ["Tight", "Moderate", "Loose"],
                                      'Infeasible Programs Rate',
                                      ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                      ["darkred", "red", "tomato", "orange"],
                                      OUTPUT_PATH + '/charts/' + env_size + "Arch/Random/" + random_task_set + "_infeasible_rate.png")

                    plot_merged(times,
                                ["Tight", "Moderate", "Loose"],
                                'Optimization Time (S)',
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["darkred", "red", "tomato", "orange"],
                                OUTPUT_PATH + '/charts/' + env_size + "Arch/Random/" + random_task_set + "_overall_time_comparison.png")

            elif task_set == "RandomDAG":
                for graph_size in randomDAG_graph_sizes:
                    times = [[], [], []]
                    overall_random_energy_consumptions = [[], [], []]
                    avg_random_energy_consumptions = [[], [], []]
                    random_rates = [[], [], []]
                    timeout_rates = [[], [], []]
                    infeasible_rates = [[], [], []]

                    for deadline_idx in range(len(deadlines)):
                        for method_idx in range(len(methods)):
                            energy_consumption = pd.read_csv(
                                OUTPUT_PATH + '/' + env_size + 'Arch/' + deadlines[deadline_idx] + 'Deadline/' +
                                methods[
                                    method_idx] + '/RandomDAG/' + graph_size + 'Graph/Average_consumed_energy.csv')
                            overall_random_energy_consumptions[deadline_idx].append(energy_consumption.iloc[0]["Overall"])

                            makespan = deadline_df.loc[deadline_df["Graph"] == "RandomDAG"].loc[
                                deadline_df["GraphSize"] == graph_size].loc[
                                deadline_df["Method"] == methods[method_idx]].loc[
                                deadline_df["EnvSize"] == env_size].iloc[
                                0]["Avg_" + deadlines[deadline_idx]]
                            avg_random_energy_consumptions[deadline_idx].append(
                                energy_consumption.iloc[0]["Overall"] / makespan)

                            time = pd.read_csv(
                                OUTPUT_PATH + '/' + env_size + 'Arch/' + deadlines[deadline_idx] + 'Deadline/' +
                                methods[
                                    method_idx] + '/RandomDAG/' + graph_size + 'Graph/Average_time.csv')
                            times[deadline_idx].append(time.iloc[0]["Time"])
                            random_rates[deadline_idx].append(
                                round(((30 - time.iloc[0]["infeasible"] - time.iloc[0]["timeout"]) / 30) * 100))
                            timeout_rates[deadline_idx].append(round(((time.iloc[0]["timeout"]) / 30) * 100))
                            infeasible_rates[deadline_idx].append(round(((time.iloc[0]["infeasible"]) / 30) * 100))

                    plot_merged(overall_random_energy_consumptions,
                                ["Tight", "Moderate", "Loose"],
                                'Overall Energy',
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["darkred", "red", "tomato", "orange"],
                                OUTPUT_PATH + '/charts/' + env_size + 'Arch/RandomDAG/' + graph_size + '_overall_energy_comparison.png')

                    plot_merged(avg_random_energy_consumptions,
                                ["Tight", "Moderate", "Loose"],
                                'Average Energy',
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["darkred", "red", "tomato", "orange"],
                                OUTPUT_PATH + '/charts/' + env_size + 'Arch/RandomDAG/' + graph_size + '_average_energy_comparison.png')

                    rates_plot_merged(random_rates,
                                      ["Tight", "Moderate", "Loose"],
                                      'Success Rate',
                                      ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                      ["darkred", "red", "tomato", "orange"],
                                        OUTPUT_PATH + '/charts/' + env_size + 'Arch/RandomDAG/' + graph_size + "_success_rate.png")

                    rates_plot_merged(timeout_rates,
                                      ["Tight", "Moderate", "Loose"],
                                      'Timeout Rate',
                                      ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                      ["darkred", "red", "tomato", "orange"],
                                        OUTPUT_PATH + '/charts/' + env_size + 'Arch/RandomDAG/' + graph_size + "_timeout_rate.png")

                    rates_plot_merged(infeasible_rates,
                                      ["Tight", "Moderate", "Loose"],
                                      'Infeasible Programs Rate',
                                      ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                      ["darkred", "red", "tomato", "orange"],
                                           OUTPUT_PATH + '/charts/' + env_size + 'Arch/RandomDAG/' + graph_size + "_infeasible_rate.png")

                    plot_merged(times,
                                ["Tight", "Moderate", "Loose"],
                                'Optimization Time (S)',
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["darkred", "red", "tomato", "orange"],
                                     OUTPUT_PATH + '/charts/' + env_size + 'Arch/RandomDAG/' + graph_size + "_overall_time_comparison.png")
