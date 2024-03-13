from taskGraphGenerator import RandomTaskGenerator


MIN_EDGE_WEIGHTS = [1, 10, 20]
MAX_EDGE_WEIGHTS = [10, 20, 30]

if __name__ == "__main__":
    # Generate small graphs with 3 or 4 nodes per graph
    small_graph_generator = RandomTaskGenerator(100, ['MEMORY', 'FMULT', 'SIMD'], [0.4, 0.5, 0.6], [3, 4])
    small_graph_generator.generate_graph(10, 12, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/NewTasks/RandomGraphs/smallGraph/")
    small_graph_generator.generate_graph(10, 6, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/NewTasks/RandomGraphs/smallGraph/")

    # Generate medium graphs with 5 or 6 nodes per graph
    medium_graph_generator = RandomTaskGenerator(100, ['MEMORY', 'FMULT', 'SIMD'], [0.4, 0.5, 0.6], [5, 6])

    medium_graph_generator.generate_graph(10, 12, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/NewTasks/RandomGraphs/mediumGraph/")
    medium_graph_generator.generate_graph(10, 6, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/NewTasks/RandomGraphs/mediumGraph/")

    # Generate large graphs with 7 or 8 nodes per graph
    large_graph_generator = RandomTaskGenerator(100, ['MEMORY', 'FMULT', 'SIMD'], [0.4, 0.5, 0.6], [7, 8])

    large_graph_generator.generate_graph(10, 12, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/NewTasks/RandomGraphs/largeGraph/")
    large_graph_generator.generate_graph(10, 6, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/NewTasks/RandomGraphs/largeGraph/")
