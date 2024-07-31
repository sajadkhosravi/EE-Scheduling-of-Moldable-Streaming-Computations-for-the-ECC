import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import os


class DAGGenerator:
    def __init__(self, max_workload, task_types, probabilities, graph_sizes, rand_seed=2502):
        self.max_workload = max_workload
        self.task_types = task_types
        self.probabilities = probabilities
        self.graph_sizes = graph_sizes
        self.rand_seed = rand_seed

    def generate_task(self, num_cores, fraction=1):
        task = {
            "id": 0,
            "workload": random.choice(range(1, int((self.max_workload * fraction)) + 1)),
            "type": random.choice(self.task_types)
        }
        max_width_log = (random.choice(range(int(math.log2(num_cores)) + 1)))
        task["max_width"] = 2 ** max_width_log
        while task["workload"] / task["max_width"] > self.max_workload / (num_cores / 2):
            # Obtain new values to avoid tasks with huge workloads and small maximum width (obviously, this leads to skewed distribution)
            task["workload"] = random.choice(range(1, (self.max_workload * fraction) + 1))
            max_width_log = (random.choice(range(int(math.log2(num_cores)) + 1)))
            task["max_width"] = 2 ** max_width_log
        return task

    def generate_task_set(self, num_tasks, num_cores, source_fraction, sink_fraction):
        tasks = []

        source_task = self.generate_task(num_cores, source_fraction)
        source_task["id"] = 0
        tasks.append(source_task)

        for j in range(1, num_tasks - 1):
            task = self.generate_task(num_cores)
            task["id"] = j
            tasks.append(task)

        sink_task = self.generate_task(num_cores, sink_fraction)
        sink_task["id"] = num_tasks - 1
        tasks.append(sink_task)

        return tasks

    def generate_dag(self, node_count, probability):
        random_dag = nx.gnp_random_graph(node_count - 2, probability, directed=True)

        while not nx.is_directed_acyclic_graph(random_dag):
            random_dag = nx.gnp_random_graph(node_count - 2, probability, directed=True)

        tasks_with_input_degree_zero = [node for node in random_dag.nodes() if random_dag.in_degree(node) == 0]
        tasks_with_output_degree_zero = [node for node in random_dag.nodes() if random_dag.out_degree(node) == 0]

        random_dag.add_node(node_count - 2)  # Source node
        random_dag.add_node(node_count - 1)  # Sink node

        for node in tasks_with_input_degree_zero:
            random_dag.add_edge(node_count - 2, node)

        for node in tasks_with_output_degree_zero:
            random_dag.add_edge(node, node_count - 1)

        return random_dag

    def generate_edges(self, node_count, probability, edge_weights_lb, edge_weights_ub, output_path):
        random_dag = self.generate_dag(node_count, probability)
        self.draw_graph(random_dag, output_path)
        edges = []

        for edge in random_dag.edges:
            if edge[0] < node_count - 2:
                src = edge[0] + 1
            elif edge[0] == node_count - 2:
                src = 0
            else:
                src = edge[0]
            if edge[1] < node_count - 2:
                dest = edge[1] + 1
            elif edge[1] == node_count - 2:
                dest = 0
            else:
                dest = edge[1]

            edge_dict = {
                "src": src,
                "dest": dest,
                "weight": round(random.uniform(edge_weights_lb, edge_weights_ub), 4)
            }
            edges.append(edge_dict)

        return edges

    def generate_topology(self, num_tasks, num_cores, edge_probability, edge_weights_lb, edge_weights_ub,
                          source_fraction, sink_fraction, output_path):
        tasks = self.generate_task_set(num_tasks, num_cores, source_fraction, sink_fraction)
        edges = self.generate_edges(num_tasks, edge_probability, edge_weights_lb, edge_weights_ub, output_path)

        return {
            "tasks": tasks,
            "edges": edges
        }

    def draw_graph(self, graph, output_path):
        nx.draw(graph, with_labels=False, arrows=True)

        # Save the graph
        plt.savefig(output_path, format="png", bbox_inches='tight')
        plt.close()


    def generate_graph_file(self, graphs, sink_edge_weight_lb, sink_edge_weight_ub):
        # Define GraphML template
        graphml_content = """<?xml version="1.0" encoding="UTF-8"?>
                    <graphml xmlns="http://graphml.graphdrawing.org/xmlns"
                             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                             xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
                             http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
                    <!-- Created by igraph -->
                      <key id="v_workload" for="node" attr.name="workload" attr.type="double"/>
                      <key id="v_max_width" for="node" attr.name="max_width" attr.type="double"/>
                      <key id="v_task_type" for="node" attr.name="task_type" attr.type="string"/>
                      <key id="v_task_name" for="node" attr.name="task_name" attr.type="string"/>
                      <key id="v_instance" for="node" attr.name="instance" attr.type="double"/>
                      <key id="e_data_transfer" for="edge" attr.name="data_transfer" attr.type="double"/>
                      <graph id="G" edgedefault="directed">
                      </graph>
                    </graphml>"""

        last_id = 0
        for i in range(len(graphs)):
            for task in graphs[i]["tasks"]:
                node_content = f"""<node id="n{last_id + task["id"]}">
                                        <data key="v_workload">{task['workload']}</data>
                                        <data key="v_max_width">{task['max_width']}</data>
                                        <data key="v_task_type">{task['type']}</data>
                                        <data key="v_task_name">task{task['id']}</data>
                                        <data key="v_instance">{i}</data>
                                    </node>
                                    """
                graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)
            last_id += len(graphs[i]["tasks"])

        common_sink_id = last_id
        node_content = f"""<node id="n{common_sink_id}">
                                <data key="v_workload">1</data>
                                <data key="v_max_width">1</data>
                                <data key="v_task_type">"MEMORY"</data>
                                <data key="v_task_name">sink</data>
                                <data key="v_instance">{len(graphs)}</data>
                            </node>
                            """
        graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)

        last_id = 0
        for i in range(len(graphs)):
            instance_sink_id = 0
            for edge in graphs[i]["edges"]:
                if last_id + edge["dest"] > instance_sink_id:
                    instance_sink_id = last_id + edge["dest"]
                node_content = f"""<edge source="n{last_id + edge["src"]}" target="n{last_id + edge["dest"]}">
                                        <data key="e_data_transfer">{edge["weight"]}</data>
                                    </edge>
                                    """
                graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)
            last_id += len(graphs[i]["tasks"])
            node_content = f"""<edge source="n{instance_sink_id}" target="n{common_sink_id}">
                                    <data key="e_data_transfer">{round(random.uniform(sink_edge_weight_lb, 
                                                                                      sink_edge_weight_ub), 4)}</data>
                               </edge>
                               """
            graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)

        return graphml_content

    def generate_graph(self, num_instances, num_task_set, num_cores, edge_weight_lb, edge_weight_ub, output_path):
        for instance_id in range(num_instances):
            try:
                os.makedirs(output_path + "img/")
            except:
                pass
            graphs = []

            n = int((num_task_set / len(self.graph_sizes)) // len(self.probabilities))
            index = 0
            for i in range(n):
                for graph_size in self.graph_sizes:
                    for probability in self.probabilities:
                        graphs.append(self.generate_topology(graph_size, num_cores, probability, edge_weight_lb,
                                                             edge_weight_ub, 0.1, 1,
                                                             output_path + "img/" + "graph_" + str(index) + "_n" + str(
                                                                 graph_size) + "_" + str(instance_id) + ".png"))
                        index += 1

            graphml_content = self.generate_graph_file(graphs, edge_weight_lb, edge_weight_ub)

            with open(output_path + "graph_ts" + str(num_task_set) + "_task_sets_" + str(instance_id) + ".graphml",
                      'w') as output_file:
                output_file.write(graphml_content)
