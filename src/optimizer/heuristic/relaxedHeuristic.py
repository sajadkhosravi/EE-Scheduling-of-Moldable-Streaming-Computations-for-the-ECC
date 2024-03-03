from .baseHeuristic import Heuristic

CLOUD_ID = 0

class RelaxedHeuristic(Heuristic):
    def __init__(self, task_graph, compute_resource, network_info, execution_time_multipliers, power_info):
        super().__init__(task_graph, compute_resource, network_info, execution_time_multipliers, power_info)
        self.bandwidth_edge_to_edge = network_info["bandwidth_edge_to_edge"]
        self.power_edge_to_edge = network_info["power_edge_to_edge"]
        self.bandwidth_device_to_cloud = network_info["bandwidth_device_to_cloud"]
        self.power_device_to_cloud = network_info["power_device_to_cloud"]

        self.upload_bandwidth_edge_edge = network_info["upload_bandwidth_edge_edge"]
        self.download_bandwidth_edge_edge = network_info["download_bandwidth_edge_edge"]

        self.edges = []
        self.edge_weights = {}
        for i in range(len(task_graph.es)):
            source = task_graph.es[i].source
            target = task_graph.es[i].target
            self.ids.append(self.num_tasks)
            self.workloads.append(0)
            self.max_widths.append(1)
            self.task_types.append("TRANSFER")
            self.task_names.append("TRANSFER_" + str(i))
            self.instances.append(self.instances[source])

            self.edges.append((source, self.num_tasks))
            # Edge weights are data transfers in MB
            self.edge_weights[(source, self.num_tasks)] = task_graph.es[i]['data_transfer']

            self.edges.append((self.num_tasks, target))
            # Edge weights are data transfers in MB
            self.edge_weights[(self.num_tasks, target)] = task_graph.es[i]['data_transfer']

            self.num_tasks += 1

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
        if self.get_node_type(orig_node) == 1 and self.get_node_type(dest_node) == 2:
            return (self.bandwidth_device_to_cloud / 8) * deadline
        if self.get_node_type(orig_node) == 1 and self.get_node_type(dest_node) == 1:
            return (self.bandwidth_edge_to_edge / 8) * deadline
        raise ValueError("Implausible node pair discovered in bandwidth request.")

    def get_node_upload_links_volume(self, node, dest_type):
        # Link exists, determine type of nodes
        if self.get_node_type(node) == 0 and dest_type == 1:
                # Volume depends on bandwidth and round length
                # Bandwidth is in MBit/s, deadline in s, volume in MB
            return (self.upload_bandwidth_device / 8) * self.deadline
        if self.get_node_type(node) == 1 and dest_type == 2:
            return (self.upload_bandwidth_edge_cloud / 8) * self.deadline
        if self.get_node_type(node) == 1 and dest_type == 1:
            return (self.upload_bandwidth_edge_edge / 8) * self.deadline
        return 0.0

    def get_node_download_links_volume(self, node, src_type):
        if self.get_node_type(node) == 1 and src_type == 0:
                # Volume depends on bandwidth and round length
                # Bandwidth is in MBit/s, deadline in s, volume in MB
            return (self.download_bandwidth_edge_device / 8) * self.deadline
        if self.get_node_type(node) == 2 and src_type == 1:
            return (self.download_bandwidth_cloud / 8) * self.deadline
        if self.get_node_type(node) == 1 and src_type == 1:
            return (self.download_bandwidth_edge_edge / 8) * self.deadline
        return 0.0


    def get_comm_energy(self, orig_node, dest_node, data_amount):
        # data to transfer is given in MB
        # Bandwidth is in MBit/s, power in W
        if orig_node == dest_node:
            return 0.0
        elif self.get_node_type(orig_node) == 0 and self.get_node_type(dest_node) == 1:
            bandwidth = self.bandwidth_device_to_edge
            power = self.power_device_to_edge
        elif self.get_node_type(orig_node) == 1 and self.get_node_type(dest_node) == 2:
            bandwidth = self.bandwidth_edge_to_cloud
            power = self.power_edge_to_cloud
        elif self.get_node_type(orig_node) == 1 and self.get_node_type(dest_node) == 1:
            bandwidth = self.bandwidth_edge_to_edge
            power = self.power_edge_to_edge
        else:
            raise ValueError("Implausible node pair discovered in bandwidth request.")
        comm_duration = data_amount / (bandwidth / 8)
        # Communication energy is in J
        return comm_duration * power
