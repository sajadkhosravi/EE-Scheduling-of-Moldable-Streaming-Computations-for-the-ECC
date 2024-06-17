from DAGGenerator import DAGGenerator
import networkx as nx

class ChainOfTaskGenerator(DAGGenerator):
    def __init__(self, max_workload, task_types, probabilities, graph_sizes, rand_seed=2502):
        super().__init__(max_workload, task_types, probabilities, graph_sizes, rand_seed)

    def generate_dag(self, node_count, probability):
        cot_graph = nx.DiGraph()

        cot_graph.add_node(0)
        cot_graph.add_node(node_count - 2) # Source node
        cot_graph.add_node(node_count - 1) # Sink node

        cot_graph.add_edge(node_count - 2, 0)

        for i in range(1, node_count - 2):
            cot_graph.add_node(i)
            cot_graph.add_edge(i-1, i)

        cot_graph.add_edge(node_count - 3, node_count - 1)

        return cot_graph
