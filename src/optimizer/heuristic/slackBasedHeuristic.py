from ..optimizer import Optimizer


# Create a vector slack for each node
# Create a vector slack for each communication link
# Assign function
# Seeding phase
# Rescaling phase


class SlackBasedHeuristic(Optimizer):
    def __init__(self, task_graph, compute_resource, network_info, execution_time_multipliers, power_info):
        super().__init__(task_graph, compute_resource, network_info, execution_time_multipliers, power_info)

    def get_connected_nodes(self, predecessor_node):
        connected_nodes_by_level = []
        for ind in range(3 - self.get_node_type(predecessor_node)):
            connected_nodes_by_level.append([])
        for u, v in self.network_links:
            if u == predecessor_node:
                if self.get_node_type(u) <= self.get_node_type(v):
                    connected_nodes_by_level[self.get_node_type(v) - self.get_node_type(u)].append(v)
            elif v == predecessor_node:
                if self.get_node_type(v) <= self.get_node_type(u):
                    connected_nodes_by_level[self.get_node_type(u) - self.get_node_type(v)].append(u)

        return connected_nodes_by_level

    def select_node(self, available_node):
        for i in range(len(available_node)):
            if available_node[i] != -1:
                node = available_node[i]
                available_node[i] = -1
                return node
        return -1

    def select_core_group(self, node, task):
        #TODO: implement selection algorithm
        return self.num_groups - 1


    def assign(self, node, core_group, task):
        pass

    def optimize_task(self, task_id):
        connected_node = self.get_connected_nodes(3)
        for layer_node in connected_node:
            if len(layer_node) > 0:
                node = self.select_node(layer_node)
                if node != -1:
                    core_group = self.select_core_group(node, task_id)


    def optimize(self):

        for task_id in self.ids:
            self.optimize_task(task_id)


        arr2 = self.get_connected_nodes(8)
        print(arr2)


    def generate_result(self, output_path):
        pass


