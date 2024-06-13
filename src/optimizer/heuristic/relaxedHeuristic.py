from .strictHeuristic import Heuristic

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

    def get_node_outgoing_links_volume(self, node, dest_type):
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

    def get_node_incoming_links_volume(self, node, src_type):
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
            return float('inf')
        comm_duration = data_amount / (bandwidth / 8)
        # Communication energy is in J
        return comm_duration * power

    def is_assignable(self, node, core_group, task, predecessors_info, required_time, upload_channel_slack,
                      download_channel_slack, workload_slack):
        workload_assignment_status = True
        channel_assignment_status = True

        for i in range(len(predecessors_info)):
            if node == predecessors_info.iloc[i]["Node"]:
                continue
            remained_upload_channel_volume = [0.0, 0.0]
            if self.get_node_type(predecessors_info.iloc[i]["Node"]) == 1:
                remained_upload_channel_volume[1] = upload_channel_slack[predecessors_info.iloc[i]["Node"]][2] - self.edge_weights[(predecessors_info.iloc[i]["Task"], task)]
                remained_upload_channel_volume[0] = upload_channel_slack[predecessors_info.iloc[i]["Node"]][1] - self.edge_weights[(predecessors_info.iloc[i]["Task"], task)]
            else:
                remained_upload_channel_volume[0] = upload_channel_slack[predecessors_info.iloc[i]["Node"]][self.get_node_type(node)] - self.edge_weights[(predecessors_info.iloc[i]["Task"], task)]

            remained_download_channel_volume = download_channel_slack[node][self.get_node_type(predecessors_info.iloc[i]["Node"])] - self.edge_weights[(predecessors_info.iloc[i]["Task"], task)]

            if (remained_upload_channel_volume[0] < 0 and remained_upload_channel_volume[1] < 0) or remained_download_channel_volume < 0:
                channel_assignment_status = False
                break
            if self.get_node_type(predecessors_info.iloc[i]["Node"]) == 1:
                upload_channel_slack[predecessors_info.iloc[i]["Node"]][1] = remained_upload_channel_volume[0]
                upload_channel_slack[predecessors_info.iloc[i]["Node"]][2] = remained_upload_channel_volume[1]
            else:
                upload_channel_slack[predecessors_info.iloc[i]["Node"]][self.get_node_type(node)] = remained_upload_channel_volume[0]
            download_channel_slack[node][self.get_node_type(predecessors_info.iloc[i]["Node"])] = remained_download_channel_volume

        core_groups = [core_group]
        core_groups = core_groups + self.get_parent_core_groups(core_group)
        core_groups = core_groups + self.get_child_core_groups(core_group, self.num_groups[node])

        for i in core_groups:
            if workload_slack[i - 1] - required_time < 0:
                workload_assignment_status = False
                break
            else:
                workload_slack[i - 1] = workload_slack[i - 1] - required_time

        return workload_assignment_status, channel_assignment_status