from DAGGenerator import DAGGenerator
import networkx as nx


class IndependentTaskGraphGenerator(DAGGenerator):
    def __init__(self, max_workload, task_types, probabilities, graph_sizes, rand_seed=2502):
        super().__init__(max_workload, task_types, probabilities, graph_sizes, rand_seed)

    def generate_dag(self, node_count, probability):
        itg_graph = nx.DiGraph()

        itg_graph.add_node(node_count - 2) # Source node
        itg_graph.add_node(node_count - 1) # Sink node

        for i in range(0, node_count - 2):
            itg_graph.add_node(i)
            itg_graph.add_edge(node_count - 2, i)
            itg_graph.add_edge(i, node_count - 1)

        return itg_graph
