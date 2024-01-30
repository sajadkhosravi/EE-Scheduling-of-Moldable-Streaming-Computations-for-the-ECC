from ..optimizer import Optimizer


# Create a vector slack for each node
# Create a vector slack for each communication link
# Assign function
# Seeding phase
# Rescaling phase


class SlackBasedHeuristic(Optimizer):
    def __init__(self, task_graph, compute_resource, network_info, execution_time_multipliers, power_info):
        super().__init__(task_graph, compute_resource, network_info, execution_time_multipliers, power_info)
        self.bandwidth_edge_to_edge = network_info["bandwidth_edge_to_edge"]
        self.power_edge_to_edge = network_info["power_edge_to_edge"]
        self.bandwidth_device_to_cloud = network_info["bandwidth_device_to_cloud"]
        self.power_device_to_cloud = network_info["power_device_to_cloud"]
        self.workload_slack = []
        self.channel_slack = {}

    def get_link_volume(self, orig_node, dest_node, deadline):
        if orig_node == dest_node:
            return float('inf')
        if not (orig_node, dest_node) in self.network_links:
            return 0
        # Link exists, determine type of nodes
        if self.get_node_type(orig_node) == 0 and self.get_node_type(dest_node) == 1:
            # Volume depends on bandwidth and round length
            # Bandwidth is in MBit/s, deadline in s, volume in MB
            return (self.bandwidth_device_to_edge / 8) * deadline
        if self.get_node_type(orig_node) == 1 and self.get_node_type(dest_node) == 2:
            return (self.bandwidth_edge_to_cloud / 8) * deadline
        if self.get_node_type(orig_node) == 0 and self.get_node_type(dest_node) == 2:
            return (self.bandwidth_device_to_edge / 8) * deadline
        if self.get_node_type(orig_node) == 1 and self.get_node_type(dest_node) == 2:
            return (self.bandwidth_device_to_cloud / 8) * deadline
        if self.get_node_type(orig_node) == 1 and self.get_node_type(dest_node) == 1:
            return (self.bandwidth_edge_to_edge / 8) * deadline
        raise ValueError("Implausible node pair discovered in bandwidth request.")

    def slacks_init(self):
        # Initialize channel slack vector
        for u, v in self.network_links:
            self.channel_slack[str(u) + "-" + str(v)] = self.get_link_volume(u, v, self.deadline)

        # Initialize workload slack vector
        for layer in range(2, -1, -1):
            for i in range(self.nodes[layer]):
                index = i
                for j in range(layer):
                    index = index + self.nodes[j]
                workload_time_array = [self.deadline] * self.num_groups[index]
                self.workload_slack.append(workload_time_array)

    def get_connected_nodes(self, predecessor_nodes):
        connected_nodes = [[], [], []]
        connected_nodes_dict = {}
        for u, v in self.network_links:
            if u in predecessor_nodes:
                if u not in connected_nodes_dict:
                    connected_nodes_dict[u] = set()
                if self.get_node_type(u) <= self.get_node_type(v):
                    connected_nodes_dict[u].add(v)

        common_nodes = set.intersection(*connected_nodes_dict.values()) if connected_nodes_dict else set()

        common_nodes_arr = list(common_nodes)
        for node in common_nodes_arr:
            connected_nodes[self.get_node_type(node)].append(node)

        return connected_nodes

    def select_node(self, available_node):
        for i in range(len(available_node)):
            if available_node[i] != -1:
                node = available_node[i]
                available_node[i] = -1
                return node
        return -1

    def select_core_group(self, node, task):
        # TODO: implement selection algorithm
        return self.num_groups[node] - 1

    def get_parent_core_groups(self, core_group):
        core_groups = []
        while core_group > 1:
            res = core_group // 2
            core_groups.append(res)
            core_group = res

        return core_groups

    def get_child_core_groups(self, core_group, max_core_group_id):
        core_groups = []
        candidate = [core_group]
        while len(candidate) > 0:
            group_id = candidate.pop(0)
            if group_id * 2 < max_core_group_id:
                res = group_id * 2
                core_groups.append(res)
                core_groups.append(res + 1)
                candidate.append(res)
                candidate.append(res + 1)

        return core_groups

    def assign(self, node, core_group, task, predecessors_info):

        remained_volumes = []
        for predecessor in predecessors_info:
            remained_volume = self.channel_slack[str(predecessor["node"]) + "-" + str(node)] - self.edge_weights[
                (predecessor["task"], task)]
            if remained_volume < 0:
                return False
            remained_volumes.append(remained_volume)

        required_time = self.get_task_runtime(node, self.cores[node], core_group, self.workloads[task],
                                              self.max_widths[task], self.task_types[task], -1)
        core_groups = [core_group]
        core_groups = core_groups + self.get_parent_core_groups(core_group)
        core_groups = core_groups + self.get_child_core_groups(core_group, self.num_groups[node])

        temp = self.workload_slack[node].copy()
        for i in core_groups:
            if temp[i - 1] - required_time < 0:
                return False
            else:
                temp[i - 1] = temp[i - 1] - required_time

        self.workload_slack[node] = temp
        for index in range(len(predecessors_info)):
            self.channel_slack[str(predecessors_info[index]["node"]) + "-" + str(node)] = remained_volumes[index]
        return True

    def optimize_task(self, task_id, predecessors_info):
        # TODO: improve this part
        predecessor_nodes = []
        for predecessor in predecessors_info:
            predecessor_nodes.append(predecessor["node"])
        connected_node = self.get_connected_nodes(predecessor_nodes)
        assignment_info = {
            "node": -1,
            "core_group": -1
        }
        for layer_nodes in connected_node:
            for i in range(len(layer_nodes)):
                node = self.select_node(layer_nodes)
                if node != -1:
                    core_group = self.select_core_group(node, task_id)
                    if self.assign(node, core_group, task_id, predecessors_info):
                        assignment_info["node"] = node
                        assignment_info["core_group"] = core_group
                        break
            if assignment_info["node"] != -1:
                break

        print(self.get_child_core_groups(3, 7))

        print(assignment_info)

    def optimize(self):

        self.slacks_init()
        # for task_id in self.ids:
        self.optimize_task(26, [{"node": 8, "task": 22}, {"node": 1, "task": 23}])

    def generate_result(self, output_path):
        pass
