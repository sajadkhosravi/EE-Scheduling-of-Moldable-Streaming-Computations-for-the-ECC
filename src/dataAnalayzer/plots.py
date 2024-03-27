import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import sys
import math

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

    plt.figure(figsize=(10, 6))
    plt.bar(nodes, data_arr, width=0.4, label=label, align='center', alpha=0.7, color=color)
    x_labels = ['Cloud'] + [' '] + [f'L{i}' for i in range(1, size_vars[env_size]["ub_edge"])] + [' '] + [f'D{i}' for i in range(size_vars[env_size]["ub_edge"], size_vars[env_size]["nodes"] - 2)]
    plt.xticks(range(size_vars[env_size]["nodes"]), x_labels, fontsize=30, rotation=90)
    plt.xlabel('Node', fontsize=30)
    plt.ylabel('Energy', fontsize=30)
    plt.yticks(fontsize=30)
    # plt.legend()
    # plt.savefig(OUTPUT_PATH + '/charts/' + deadline + "Deadline/" + env_size + "/" + label + '_' + type + '_node_energy_comparison.svg', format="svg",
    #             bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/' + deadline + "Deadline/" + env_size + "/" + label + '_' + type + '_node_energy_comparison.png', format="png",
                bbox_inches='tight')
    plt.close()


def overall_result(data, labels, colors, output_file_name):
    max_value = max(data)
    methods = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, data, width=0.4, align='center', alpha=0.7, color=colors)

    for bar, value in zip(bars, data):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(value, 2), ha='center', va='bottom', fontsize=20)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=22)
    # plt.xlabel('Methods')
    plt.ylabel('Overall Energy', fontsize=22)
    plt.yticks(fontsize=20)
    plt.ylim(0, int(max_value * 1.3))
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_overall_node_energy_comparison.svg', format="svg",
    #             bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_overall_node_energy_comparison.png', format="png",
                bbox_inches='tight')
    plt.close()

def overall_result_merged(data, labels, colors, output_file_name):
    num_methods = len(data)
    num_values = len(data[0])

    max_value = np.max(data)
    if max_value > 8000:
        max_value = 20000
    elif max_value > 5000:
        max_value = 15000
    elif max_value > 2000:
        max_value = 10000
    else:
        max_value = 1500
    methods = np.arange(0, num_methods)

    plt.figure(figsize=(10, 6))

    bar_width = 0.2
    bar_offsets = np.linspace(-bar_width, bar_width, num_values)

    legend_labels = ['Tight', 'Moderate', 'Loose']
    for i in range(num_values):
        bars = plt.bar(methods + bar_offsets[i], [row[i] for row in data], width=bar_width, align='center',
                       alpha=0.7, color=colors[i], label=legend_labels[i])

        for bar, value in zip(bars, [row[i] for row in data]):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), " " + str(round(value, 2)),
                     ha='center', va='bottom', fontsize=28, rotation=90)

    x_labels = labels
    plt.xticks(range(num_methods), x_labels, fontsize=30)
    plt.ylabel('Overall Energy', fontsize=30)
    plt.yticks(fontsize=28)
    plt.ylim(0, max_value)
    plt.legend(fontsize=22, loc='upper left', ncol=3)

    plt.savefig(OUTPUT_PATH + '/charts/' + output_file_name + '_overall_node_energy_comparison.png', format="png",
                bbox_inches='tight')
    plt.close()


def time_plot(data, labels, colors, output_file_name):
    max_value = max(data)
    methods = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, data, width=0.4, align='center', alpha=0.7, color=colors)

    for bar, value in zip(bars, data):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(value, 2), ha='center', va='bottom',
                 fontsize=20)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=22)
    # plt.xlabel('Methods')
    plt.ylabel('Optimization Time (S)', fontsize=22)
    plt.yticks(fontsize=20)
    plt.ylim(0, int(max_value * 2))
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_time_comparison.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_time_comparison.png', format="png", bbox_inches='tight')
    plt.close()


def time_plot_merged(data, labels, colors, output_file_name):
    num_methods = len(data)
    num_values = len(data[0])

    max_value = np.max(data)
    methods = np.arange(0, num_methods)

    plt.figure(figsize=(10, 6))
    bar_width = 0.2
    bar_offsets = np.linspace(-bar_width, bar_width, num_values)
    legend_labels = ['Tight', 'Moderate', 'Loose']

    for i in range(num_values):
        bars = plt.bar(methods + bar_offsets[i], [row[i] for row in data], width=bar_width, align='center',
                       alpha=0.7, color=colors[i], label=legend_labels[i])

        for bar, value in zip(bars, [row[i] for row in data]):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), " " + str(round(value, 2)),
                     ha='center', va='bottom', fontsize=28, rotation=90)
    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=30)
    # plt.xlabel('Methods')
    plt.ylabel('Optimization Time (S)', fontsize=30)
    plt.yticks(fontsize=28)
    plt.ylim(0, math.ceil(max_value * 1.5))
    plt.legend(fontsize=22, loc='upper right')
    formatter = FuncFormatter(lambda x, _: '{:.1f}'.format(x))
    plt.gca().yaxis.set_major_formatter(formatter)

    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_time_comparison.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/' + output_file_name + '_time_comparison.png', format="png", bbox_inches='tight')
    plt.close()


def success_plot(data, labels, colors, output_file_name):
    methods = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, data, width=0.3, align='center', alpha=0.7, color=colors)

    for bar, value in zip(bars, data):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), str(round(value, 2)) + "%", ha='center', va='bottom', fontsize=18)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=22)
    # plt.xlabel('Methods')
    plt.ylabel('Success Rate', fontsize=22)
    plt.yticks(fontsize=20)
    plt.ylim(0, 100)
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_success_rate.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_success_rate.png', format="png", bbox_inches='tight')
    plt.close()

def success_plot_merged(data, labels, colors, output_file_name):
    num_values = len(data[0])

    methods = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bar_width = 0.2
    bar_offsets = np.linspace(-bar_width, bar_width, num_values)
    legend_labels = ['Tight Deadline', 'Moderate Deadline', 'Loose Deadline']

    for i in range(num_values):
        bars = plt.bar(methods + bar_offsets[i], [row[i] for row in data], width=bar_width, align='center',
                       alpha=0.7, color=colors[i], label=legend_labels[i])

        for bar, value in zip(bars, [row[i] for row in data]):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), " " + str(round(value, 2)) + "%",
                     ha='center', va='bottom', fontsize=28, rotation=90)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=30)
    # plt.xlabel('Methods')
    plt.ylabel('Success Rate', fontsize=30)
    plt.yticks(fontsize=28)
    plt.ylim(0, 100)
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_success_rate.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_success_rate.png', format="png", bbox_inches='tight')
    plt.close()


def timeout_plot_merged(data, labels, colors, output_file_name):
    num_values = len(data[0])

    methods = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bar_width = 0.2
    bar_offsets = np.linspace(-bar_width, bar_width, num_values)
    legend_labels = ['Tight Deadline', 'Moderate Deadline', 'Loose Deadline']

    for i in range(num_values):
        bars = plt.bar(methods + bar_offsets[i], [row[i] for row in data], width=bar_width, align='center',
                       alpha=0.7, color=colors[i], label=legend_labels[i])

        for bar, value in zip(bars, [row[i] for row in data]):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), " " + str(round(value, 2)) + "%",
                     ha='center', va='bottom', fontsize=28, rotation=90)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=30)
    # plt.xlabel('Methods')
    plt.ylabel('Timeout Rate', fontsize=30)
    plt.yticks(fontsize=28)
    plt.ylim(0, 100)
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_success_rate.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_timeout_rate.png', format="png", bbox_inches='tight')
    plt.close()

def infeasible_plot_merged(data, labels, colors, output_file_name):
    num_values = len(data[0])

    methods = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bar_width = 0.2
    bar_offsets = np.linspace(-bar_width, bar_width, num_values)
    legend_labels = ['Tight Deadline', 'Moderate Deadline', 'Loose Deadline']

    for i in range(num_values):
        bars = plt.bar(methods + bar_offsets[i], [row[i] for row in data], width=bar_width, align='center',
                       alpha=0.7, color=colors[i], label=legend_labels[i])

        for bar, value in zip(bars, [row[i] for row in data]):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), " " + str(round(value, 2)) + "%",
                     ha='center', va='bottom', fontsize=28, rotation=90)

    x_labels = labels
    plt.xticks(range(len(data)), x_labels, fontsize=30)
    # plt.xlabel('Methods')
    plt.ylabel('Infeasible Programs Rate', fontsize=30)
    plt.yticks(fontsize=28)
    plt.ylim(0, 100)
    # plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_success_rate.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/'+ output_file_name +'_infeasible_rate.png', format="png", bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please specify output directory!")
        sys.exit(1)

    OUTPUT_PATH = sys.argv[1]

    env_sizes = ["small", "medium"]
    deadlines = ["Medium", "Long", "VeryLong"]
    new_deadlines = ["Tight", "Moderate", "Loose"]
    random_tasks = ["RandomChain", "RandomFullyParallel"]
    graph_sizes = ["large", "medium", "small"]

    for env_size in env_sizes:
        overall_energy_consumptions = [[], [], [], []]
        times = [[], [], [], []]
        for deadline in deadlines:

            # Overall Energy
            overall_base = pd.read_csv(OUTPUT_PATH + '/Base/' + deadline + 'Deadline/T4/' + env_size + '/consumed_energy.csv')
            overall_relaxed = pd.read_csv(OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/T4/' + env_size + '/consumed_energy.csv')
            overall_base_heuristic = pd.read_csv(OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/consumed_energy.csv')
            overall_relaxed_heuristic = pd.read_csv(OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/consumed_energy.csv')

            overall_energy_consumptions[0].append(overall_base.iloc[0]["Overall"])
            overall_energy_consumptions[1].append(overall_relaxed.iloc[0]["Overall"])
            overall_energy_consumptions[2].append(overall_base_heuristic.iloc[0]["Overall"])
            overall_energy_consumptions[3].append(overall_relaxed_heuristic.iloc[0]["Overall"])

            time_base = pd.read_csv(OUTPUT_PATH + '/Base/' + deadline + 'Deadline/T4/' + env_size + '/time.csv')
            time_relaxed = pd.read_csv(OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/T4/' + env_size + '/time.csv')
            time_base_heuristic = pd.read_csv(OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/time.csv')
            time_relaxed_heuristic = pd.read_csv(OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/T4/' + env_size + '/time.csv')

            times[0].append(time_base.iloc[0]["Time"])
            times[1].append(time_relaxed.iloc[0]["Time"])
            times[2].append(time_base_heuristic.iloc[0]["Time"])
            times[3].append(time_relaxed_heuristic.iloc[0]["Time"])

        overall_result_merged(overall_energy_consumptions,
                           ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                           ["red", "tomato", "orange"], env_size + "/SDE")

        time_plot_merged(times,
                         ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                         ["red", "tomato", "orange"], env_size + "/SDE")

        for random_task in random_tasks:
            times = [[], [], [], []]
            random_rates = [[], [], [], []]
            timeout_rates = [[], [], [], []]
            infeasible_rates = [[], [], [], []]
            overall_random_energy_consumptions = [[], [], [], []]
            for deadline in deadlines:
                overall_random_base = pd.read_csv(
                    OUTPUT_PATH + '/Base/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_consumed_energy.csv')
                overall_random_relaxed = pd.read_csv(
                    OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_consumed_energy.csv')
                overall_random_base_heuristic = pd.read_csv(
                    OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_consumed_energy.csv')
                overall_random_relaxed_heuristic = pd.read_csv(
                    OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/Random/' + env_size + '/'+random_task+'_consumed_energy.csv')

                overall_random_energy_consumptions[0].append(overall_random_base.iloc[0]["Overall"])
                overall_random_energy_consumptions[1].append(overall_random_relaxed.iloc[0]["Overall"])
                overall_random_energy_consumptions[2].append(overall_random_base_heuristic.iloc[0]["Overall"])
                overall_random_energy_consumptions[3].append(overall_random_relaxed_heuristic.iloc[0]["Overall"])

                time_base = pd.read_csv(OUTPUT_PATH + '/Base/' + deadline + 'Deadline/Random/' + env_size + '/' + random_task + '_time.csv')
                time_relaxed = pd.read_csv(
                    OUTPUT_PATH + '/Relaxed/' + deadline + 'Deadline/Random/' + env_size + '/' + random_task + '_time.csv')
                time_base_heuristic = pd.read_csv(
                    OUTPUT_PATH + '/BaseHeuristic/' + deadline + 'Deadline/Random/' + env_size + '/' + random_task + '_time.csv')
                time_relaxed_heuristic = pd.read_csv(
                    OUTPUT_PATH + '/RelaxedHeuristic/' + deadline + 'Deadline/Random/' + env_size + '/' + random_task + '_time.csv')

                times[0].append(time_base.iloc[0]["Time"])
                times[1].append(time_relaxed.iloc[0]["Time"])
                times[2].append(time_base_heuristic.iloc[0]["Time"])
                times[3].append(time_relaxed_heuristic.iloc[0]["Time"])

                random_rates[0].append(round(((30 - time_base.iloc[0]["infeasible"] - time_base.iloc[0]["timeout"]) / 30) * 100))
                random_rates[1].append(round(((30 - time_relaxed.iloc[0]["infeasible"] - time_relaxed.iloc[0]["timeout"]) / 30) * 100))
                random_rates[2].append(round(((30 - time_base_heuristic.iloc[0]["infeasible"] - time_base_heuristic.iloc[0]["timeout"]) / 30) * 100))
                random_rates[3].append(round(((30 - time_relaxed_heuristic.iloc[0]["infeasible"] - time_relaxed_heuristic.iloc[0]["timeout"]) / 30) * 100))

                timeout_rates[0].append(round(((time_base.iloc[0]["timeout"]) / 30) * 100))
                timeout_rates[1].append(round(((time_relaxed.iloc[0]["timeout"]) / 30) * 100))
                timeout_rates[2].append(round(((time_base_heuristic.iloc[0]["timeout"]) / 30) * 100))
                timeout_rates[3].append(round(((time_relaxed_heuristic.iloc[0]["timeout"]) / 30) * 100))

                infeasible_rates[0].append(round(((time_base.iloc[0]["infeasible"]) / 30) * 100))
                infeasible_rates[1].append(round(((time_relaxed.iloc[0]["infeasible"]) / 30) * 100))
                infeasible_rates[2].append(round(((time_base_heuristic.iloc[0]["infeasible"]) / 30) * 100))
                infeasible_rates[3].append(round(((time_relaxed_heuristic.iloc[0]["infeasible"]) / 30) * 100))

            success_plot_merged(random_rates, ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                         ["red", "tomato", "orange"],
                                         env_size + "/" + random_task)

            timeout_plot_merged(timeout_rates,
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["red", "tomato", "orange"],
                                env_size + "/" + random_task)

            infeasible_plot_merged(infeasible_rates,
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["red", "tomato", "orange"],
                                env_size + "/" + random_task)


            overall_result_merged(overall_random_energy_consumptions,
                               ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                               ["red", "tomato", "orange"],
                               env_size + "/" + random_task)

            time_plot_merged(times,
                             ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                             ["red", "tomato", "orange"], env_size + "/" + random_task)

        for graph_size in graph_sizes:
            times = [[], [], [], []]
            overall_random_energy_consumptions = [[], [], [], []]
            random_rates = [[], [], [], []]
            timeout_rates = [[], [], [], []]
            infeasible_rates = [[], [], [], []]
            for deadline in new_deadlines:
                overall_random_base = pd.read_csv(
                    OUTPUT_PATH + '/RandomDAG/Base/' + deadline + '/Random/' + graph_size + "Graph/" + env_size + '/Average_consumed_energy.csv')
                overall_random_relaxed = pd.read_csv(
                    OUTPUT_PATH + '/RandomDAG/Relaxed/' + deadline + '/Random/' + graph_size + "Graph/" + env_size + '/Average_consumed_energy.csv')
                overall_random_base_heuristic = pd.read_csv(
                    OUTPUT_PATH + '/RandomDAG/BaseHeuristic/' + deadline + '/Random/' + graph_size + "Graph/" + env_size + '/Average_consumed_energy.csv')
                overall_random_relaxed_heuristic = pd.read_csv(
                    OUTPUT_PATH + '/RandomDAG/RelaxedHeuristic/' + deadline + '/Random/' + graph_size + "Graph/" + env_size + '/Average_consumed_energy.csv')

                overall_random_energy_consumptions[0].append(overall_random_base.iloc[0]["Overall"])
                overall_random_energy_consumptions[1].append(overall_random_relaxed.iloc[0]["Overall"])
                overall_random_energy_consumptions[2].append(overall_random_base_heuristic.iloc[0]["Overall"])
                overall_random_energy_consumptions[3].append(overall_random_relaxed_heuristic.iloc[0]["Overall"])



                time_random_base = pd.read_csv(OUTPUT_PATH + '/RandomDAG/Base/' + deadline + '/Random/' + graph_size + "Graph/" + env_size + '/Average_time.csv')
                time_random_relaxed = pd.read_csv(OUTPUT_PATH + '/RandomDAG/Relaxed/' + deadline + '/Random/' + graph_size + "Graph/" + env_size + '/Average_time.csv')
                time_random_base_heuristic = pd.read_csv(OUTPUT_PATH + '/RandomDAG/BaseHeuristic/' + deadline + '/Random/' + graph_size + "Graph/" + env_size + '/Average_time.csv')
                time_random_relaxed_heuristic = pd.read_csv(OUTPUT_PATH + '/RandomDAG/RelaxedHeuristic/' + deadline + '/Random/' + graph_size + "Graph/" + env_size + '/Average_time.csv')

                times[0].append(time_random_base.iloc[0]["Time"])
                times[1].append(time_random_relaxed.iloc[0]["Time"])
                times[2].append(time_random_base_heuristic.iloc[0]["Time"])
                times[3].append(time_random_relaxed_heuristic.iloc[0]["Time"])

                random_rates[0].append(round(((30 - time_random_base.iloc[0]["infeasible"] - time_random_base.iloc[0]["timeout"]) / 30) * 100))
                random_rates[1].append(round(((30 - time_random_relaxed.iloc[0]["infeasible"] - time_random_relaxed.iloc[0]["timeout"]) / 30) * 100))
                random_rates[2].append(round(((30 - time_random_base_heuristic.iloc[0]["infeasible"] - time_random_base_heuristic.iloc[0]["timeout"]) / 30) * 100))
                random_rates[3].append(round(((30 - time_random_relaxed_heuristic.iloc[0]["infeasible"] - time_random_relaxed_heuristic.iloc[0]["timeout"]) / 30) * 100))

                timeout_rates[0].append(round(((time_random_base.iloc[0]["timeout"]) / 30) * 100))
                timeout_rates[1].append(round(((time_random_relaxed.iloc[0]["timeout"]) / 30) * 100))
                timeout_rates[2].append(round(((time_random_base_heuristic.iloc[0]["timeout"]) / 30) * 100))
                timeout_rates[3].append(round(((time_random_relaxed_heuristic.iloc[0]["timeout"]) / 30) * 100))

                infeasible_rates[0].append(round(((time_random_base.iloc[0]["infeasible"]) / 30) * 100))
                infeasible_rates[1].append(round(((time_random_relaxed.iloc[0]["infeasible"]) / 30) * 100))
                infeasible_rates[2].append(round(((time_random_base_heuristic.iloc[0]["infeasible"]) / 30) * 100))
                infeasible_rates[3].append(round(((time_random_relaxed_heuristic.iloc[0]["infeasible"]) / 30) * 100))

            success_plot_merged(random_rates,
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["red", "tomato", "orange"],
                                env_size + "/RandomDAGs_" + graph_size)

            timeout_plot_merged(timeout_rates,
                                ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                ["red", "tomato", "orange"],
                                env_size + "/RandomDAGs_" + graph_size)

            infeasible_plot_merged(infeasible_rates,
                                   ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                                   ["red", "tomato", "orange"],
                                   env_size + "/RandomDAGs_" + graph_size)


            overall_result_merged(overall_random_energy_consumptions,
                               ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                               ["red", "tomato", "orange"],
                               env_size + "/RandomDAGs_" + graph_size)

            time_plot_merged(times,
                          ["ILP\nStrict", "ILP\nRelaxed", "Heuristic\nStrict", "Heuristic\nRelaxed"],
                          ["red", "tomato", "orange"], env_size + "/RandomDAGs_" + graph_size)
