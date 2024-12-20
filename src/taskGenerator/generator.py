from DAGGenerator import DAGGenerator
from chainOfTaskGenerator import ChainOfTaskGenerator
from independentTaskGraphGenerator import IndependentTaskGraphGenerator

MIN_EDGE_WEIGHTS = 1
MAX_EDGE_WEIGHTS = 2

if __name__ == "__main__":

    print("Generate small DAGs...")
    # Generate small graphs with 3 or 4 nodes per graph
    small_graph_generator = DAGGenerator(100, ['MEMORY', 'FMULT', 'SIMD'], [0.2, 0.3, 0.4], [3, 4])
    small_graph_generator.generate_graph(50, 12, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomGraphs/smallGraph/")
    small_graph_generator.generate_graph(50, 6, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomGraphs/smallGraph/")
    print("Small DAGs are generated")

    print("Generate medium DAGs...")
    # Generate medium graphs with 5 or 6 nodes per graph
    medium_graph_generator = DAGGenerator(100, ['MEMORY', 'FMULT', 'SIMD'], [0.2, 0.3, 0.4], [5, 6])

    medium_graph_generator.generate_graph(50, 12, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomGraphs/mediumGraph/")
    medium_graph_generator.generate_graph(50, 6, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomGraphs/mediumGraph/")
    print("Medium DAGs are generated")

    print("Generate large DAGs...")
    # Generate large graphs with 7 or 8 nodes per graph
    large_graph_generator = DAGGenerator(100, ['MEMORY', 'FMULT', 'SIMD'], [0.2, 0.3, 0.4], [7, 8])

    large_graph_generator.generate_graph(50, 12, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomGraphs/largeGraph/")
    large_graph_generator.generate_graph(50, 6, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomGraphs/largeGraph/")
    print("Large DAGs are generated")


    cot_generator = ChainOfTaskGenerator(100, ['MEMORY', 'FMULT', 'SIMD'], [1], [5])
    cot_generator.generate_graph(50, 12, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomChain/")
    cot_generator.generate_graph(50, 6, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomChain/")


    itg_generator = IndependentTaskGraphGenerator(100, ['MEMORY', 'FMULT', 'SIMD'], [1], [5])
    itg_generator.generate_graph(50, 12, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomIndependent/")
    itg_generator.generate_graph(50, 6, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS, "../../data/Workflows/RandomIndependent/")

    print("Generate very large DAGs...")
    # Generate large graphs with 7 or 8 nodes per graph
    very_large_graph_generator = DAGGenerator(10, ['MEMORY', 'FMULT', 'SIMD'], [0.2], [5, 6])

    very_large_graph_generator.generate_graph(10, 120, 4, MIN_EDGE_WEIGHTS, MAX_EDGE_WEIGHTS,
                                         "../../data/Workflows/RandomGraphs/verylargeGraph/")
    print("Very large DAGs are generated")