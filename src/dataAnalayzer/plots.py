import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

space_positions = [1, 6]


def node_detail(data, label, type, color):
    nodes = np.arange(0, 19)
    data_arr = []
    temp = data[type].tolist()
    i = 0
    j = 0
    while i < len(temp) + len(space_positions):
        if i in space_positions:
            data_arr.append(0)
        else:
            data_arr.append(temp[j])
            j += 1
        i += 1

    plt.figure(figsize=(10, 6))
    plt.bar(nodes, data_arr, width=0.4, label=label, align='center', alpha=0.7, color=color)
    x_labels = ['Cloud'] + [' '] + [f'L{i}' for i in range(1, 5)] + [' '] + [f'D{i}' for i in range(5, 17)]
    plt.xticks(range(19), x_labels)
    plt.xlabel('Node')
    plt.ylabel('Energy')
    plt.legend()
    plt.savefig(OUTPUT_PATH + '/charts/' + label + '_' + type + '_node_energy_comparison_4_instances.svg', format="svg",
                bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/' + label + '_' + type + '_node_energy_comparison_4_instances.png', format="png",
                bbox_inches='tight')


def overall_result(data, labels, colors):
    methods = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, data, width=0.4, align='center', alpha=0.7, color=colors)

    for bar, value in zip(bars, data):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(value, 2), ha='center', va='bottom')

    x_labels = labels
    plt.xticks(range(len(data)), x_labels)
    # plt.xlabel('Methods')
    plt.ylabel('Overall Energy')
    plt.savefig(OUTPUT_PATH + '/charts/overall_node_energy_comparison_4_instances.svg', format="svg",
                bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/overall_node_energy_comparison_4_instances.png', format="png",
                bbox_inches='tight')


def time_plot(data, labels, colors):
    methods = np.arange(0, len(data))
    plt.figure(figsize=(10, 6))
    bars = plt.bar(methods, data, width=0.4, align='center', alpha=0.7, color=colors)

    for bar, value in zip(bars, data):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), round(value, 2), ha='center', va='bottom')

    x_labels = labels
    plt.xticks(range(len(data)), x_labels)
    # plt.xlabel('Methods')
    plt.ylabel('Optimization Time')
    plt.savefig(OUTPUT_PATH + '/charts/time_comparison_4_instances.svg', format="svg", bbox_inches='tight')
    plt.savefig(OUTPUT_PATH + '/charts/time_comparison_4_instances.png', format="png", bbox_inches='tight')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please specify output directory!")
        sys.exit(1)

    OUTPUT_PATH = sys.argv[1]

    # Node Details
    node_base = pd.read_csv(OUTPUT_PATH + '\\Base\\T4\\nodes_energy.csv')
    node_relaxed = pd.read_csv(OUTPUT_PATH + '\\Relaxed\\T4\\nodes_energy.csv')
    node_symmetry_base = pd.read_csv(OUTPUT_PATH + '\\SymmetryBase\\T4\\nodes_energy.csv')
    node_symmetry_relaxed = pd.read_csv(OUTPUT_PATH + '\\SymmetryRelaxed\\T4\\nodes_energy.csv')
    node_heuristic = pd.read_csv(OUTPUT_PATH + '\\SlackHeuristic\\T4\\nodes_energy.csv')

    node_detail(node_base, 'Base', 'Overall', 'blue')
    node_detail(node_relaxed, 'Relaxed', 'Overall', 'green')
    node_detail(node_symmetry_base, 'Symmetry-Base', 'Overall', 'lightseagreen')
    node_detail(node_symmetry_relaxed, 'Symmetry-Relaxed', 'Overall', 'springgreen')
    node_detail(node_heuristic, 'Heuristic', 'Overall', 'purple')

    # Overall Energy
    overall_base = pd.read_csv(OUTPUT_PATH + '\\Base\\T4\\consumed_energy.csv')
    overall_relaxed = pd.read_csv(OUTPUT_PATH + '\\Relaxed\\T4\\consumed_energy.csv')
    overall_symmetry_base = pd.read_csv(OUTPUT_PATH + '\\SymmetryBase\\T4\\consumed_energy.csv')
    overall_symmetry_relaxed = pd.read_csv(OUTPUT_PATH + '\\SymmetryRelaxed\\T4\\consumed_energy.csv')
    overall_heuristic = pd.read_csv(OUTPUT_PATH + '\\SlackHeuristic\\T4\\consumed_energy.csv')

    overall_energy_consumptions = [
        overall_base.iloc[0]["Overall"],
        overall_symmetry_base.iloc[0]["Overall"],
        overall_relaxed.iloc[0]["Overall"],
        overall_symmetry_relaxed.iloc[0]["Overall"],
        overall_heuristic.iloc[0]["Overall"],
    ]
    overall_result(overall_energy_consumptions,
                   ["Base", "Symmetry-Base", "Relaxed", "Symmetry-Relaxed", "Heuristic"],
                   ["blue", "lightseagreen", "green", "springgreen", "purple"])

    # Optimization Time
    time_base = pd.read_csv(OUTPUT_PATH + '\\Base\\T4\\time.csv')
    time_relaxed = pd.read_csv(OUTPUT_PATH + '\\Relaxed\\T4\\time.csv')
    time_symmetry_base = pd.read_csv(OUTPUT_PATH + '\\SymmetryBase\\T4\\time.csv')
    time_symmetry_relaxed = pd.read_csv(OUTPUT_PATH + '\\SymmetryRelaxed\\T4\\time.csv')
    time_heuristic = pd.read_csv(OUTPUT_PATH + '\\SlackHeuristic\\T4\\time.csv')

    times = [
        time_base.iloc[0]["Time"],
        time_symmetry_base.iloc[0]["Time"],
        time_relaxed.iloc[0]["Time"],
        time_symmetry_relaxed.iloc[0]["Time"],
        time_heuristic.iloc[0]["Time"],
    ]
    time_plot(times,
              ["Base", "Symmetry-Base", "Relaxed", "Symmetry-Relaxed", "Heuristic"],
              ["blue", "lightseagreen", "green", "springgreen", "purple"])
