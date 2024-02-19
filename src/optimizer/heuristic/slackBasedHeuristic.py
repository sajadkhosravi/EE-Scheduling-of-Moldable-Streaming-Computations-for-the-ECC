from ..optimizer import Optimizer
from queue import Queue

import pandas as pd

# Create a vector slack for each node
# Create a vector slack for each communication link
# Assign function
# Seeding phase
# Rescaling phase


CLOUD_ID = 0
FASTEST_CORE_GROUP = 1


class SlackBasedHeuristic(Optimizer):
    def __init__(self, task_graph, compute_resource, network_info, execution_time_multipliers, power_info):
        super().__init__(task_graph, compute_resource, network_info, execution_time_multipliers, power_info)
        self.bandwidth_edge_to_edge = network_info["bandwidth_edge_to_edge"]
        self.power_edge_to_edge = network_info["power_edge_to_edge"]
        self.bandwidth_device_to_cloud = network_info["bandwidth_device_to_cloud"]
        self.power_device_to_cloud = network_info["power_device_to_cloud"]
        self.workload_slack = []
        self.channel_slack = {}
        self.active_nodes = [0] * sum(self.nodes)
        self.active_nodes[CLOUD_ID] = 1
        self.task_mapping = pd.DataFrame(columns=["Task", "Node", "Core Group", "Frequency", "IsMapped", "Instance"])

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
        elif self.get_node_type(orig_node) == 0 and self.get_node_type(dest_node) == 2:
            bandwidth = self.bandwidth_device_to_cloud
            power = self.bandwidth_device_to_cloud
        elif self.get_node_type(orig_node) == 1 and self.get_node_type(dest_node) == 1:
            bandwidth = self.bandwidth_edge_to_edge
            power = self.power_edge_to_edge
        else:
            raise ValueError("Implausible node pair discovered in bandwidth request.")
        comm_duration = data_amount / (bandwidth / 8)
        # Communication energy is in J
        return comm_duration * power

    def get_connected_nodes(self, predecessor_nodes):
        connected_nodes = [[], [], []]
        connected_nodes_dict = {}
        for u, v in self.network_links:
            if u in predecessor_nodes:
                if u not in connected_nodes_dict:
                    connected_nodes_dict[u] = set()
                    connected_nodes_dict[u].add(u)
                if self.get_node_type(u) <= self.get_node_type(v):
                    connected_nodes_dict[u].add(v)

        common_nodes = set.intersection(*connected_nodes_dict.values()) if connected_nodes_dict else set()

        common_nodes_arr = list(common_nodes)
        for node in common_nodes_arr:
            connected_nodes[self.get_node_type(node)].append(node)

        return connected_nodes

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

    def get_successor_tasks(self, task):
        connected_tasks = []

        for r, s in self.edges:
            if task == r:
                connected_tasks.append(s)

        return connected_tasks

    def get_predecessor_tasks(self, task):
        connected_tasks = []

        for r, s in self.edges:
            if task == s:
                connected_tasks.append(r)

        return connected_tasks

    def get_predecessor_tasks_mapping_info(self, task):
        predecessors = self.get_predecessor_tasks(task)
        return self.task_mapping.loc[self.task_mapping["Task"].isin(predecessors)]

    def is_ready_to_map(self, predecessors_mapping_info):
        for row in predecessors_mapping_info["IsMapped"]:
            if not row:
                return False
        return True

    def is_mapped(self, task):
        mapping_info = self.task_mapping[self.task_mapping["Task"] == task]
        return mapping_info.iloc[0]["IsMapped"]

    def is_assignable(self, node, core_group, task, predecessors_info, required_time, channel_slack, workload_slack):
        for i in range(len(predecessors_info)):
            if node == predecessors_info.iloc[i]["Node"]:
                continue
            remained_channel_volume = channel_slack[str(predecessors_info.iloc[i]["Node"]) + "-" + str(node)] - \
                                      self.edge_weights[
                                          (predecessors_info.iloc[i]["Task"], task)]
            if remained_channel_volume < 0:
                return False
            channel_slack[str(predecessors_info.iloc[i]["Node"]) + "-" + str(node)] = remained_channel_volume

        core_groups = [core_group]
        core_groups = core_groups + self.get_parent_core_groups(core_group)
        core_groups = core_groups + self.get_child_core_groups(core_group, self.num_groups[node])

        for i in core_groups:
            if workload_slack[i - 1] - required_time < 0:
                return False
            else:
                workload_slack[i - 1] = workload_slack[i - 1] - required_time

        return True

    def assign(self, node, core_group, task, predecessors_info, frequency_level):
        temp_channel_slack = self.channel_slack.copy()
        temp_workload_slack = self.workload_slack[node].copy()
        required_time = self.get_task_runtime(node, self.cores[node], core_group, self.workloads[task],
                                              self.max_widths[task], self.task_types[task], frequency_level)
        if self.is_assignable(node, core_group, task, predecessors_info, required_time, temp_channel_slack,
                              temp_workload_slack):
            self.workload_slack[node] = temp_workload_slack
            self.channel_slack[node] = temp_channel_slack
            return True

        return False

    def unassign(self, node, core_group, task, predecessors_info, frequency_level):
        required_time = self.get_task_runtime(node, self.cores[node], core_group, self.workloads[task],
                                              self.max_widths[task], self.task_types[task], frequency_level)
        core_groups = [core_group]
        core_groups = core_groups + self.get_parent_core_groups(core_group)
        core_groups = core_groups + self.get_child_core_groups(core_group, self.num_groups[node])
        for i in core_groups:
            self.workload_slack[node][i - 1] = self.workload_slack[node][i - 1] + required_time

        for i in range(len(predecessors_info)):
            if node == predecessors_info.iloc[i]["Node"]:
                continue
            self.channel_slack[str(predecessors_info.iloc[i]["Node"]) + "-" + str(node)] = self.channel_slack[str(
                predecessors_info.iloc[i]["Node"]) + "-" + str(node)] + self.edge_weights[(
                predecessors_info.iloc[i]["Task"], task)]

    def get_total_task_energy(self, src_nodes, dest_node, src_tasks, dest_task):
        execution_energy = self.get_task_energy(dest_node, self.cores[dest_node], FASTEST_CORE_GROUP,
                                                self.workloads[dest_task], self.max_widths[dest_task],
                                                self.task_types[dest_task], -1)

        comm_energy = 0
        for i in range(len(src_nodes)):
            comm_energy += self.get_comm_energy(src_nodes[i], dest_node, self.edge_weights[(src_tasks[i], dest_task)])

        total_energy = execution_energy + comm_energy
        if self.active_nodes[dest_node] == 0:
            total_energy += self.get_base_power(dest_node) * self.deadline

        return total_energy

    def get_sorted_mapping_candidate(self, available_nodes, src_nodes, src_tasks, dest_task):
        candidates = {}
        for i in range(len(available_nodes)):
            for node in available_nodes[i]:
                candidates[node] = self.get_total_task_energy(src_nodes, node, src_tasks, dest_task)

        return [t[0] for t in sorted(candidates.items())]

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

    def seeding(self):
        current_device = self.nodes[1] + self.nodes[2]
        num_nodes = sum(self.nodes)

        for task in range(0, self.num_tasks):
            if task in self.source_tasks:
                self.assign(current_device, FASTEST_CORE_GROUP, task, pd.DataFrame(), -1)
                self.task_mapping.loc[len(self.task_mapping)] = [task, current_device, FASTEST_CORE_GROUP,
                                                                 self.num_freqs[current_device] - 1, True,
                                                                 self.instances[task]]
                self.active_nodes[current_device] = 1
                current_device += 1
                if current_device >= num_nodes:
                    current_device = self.nodes[1] + self.nodes[2]
            else:
                self.assign(CLOUD_ID, FASTEST_CORE_GROUP, task, pd.DataFrame(), -1)
                is_mapped = False
                if task in self.sink_tasks:
                    is_mapped = True
                self.task_mapping.loc[len(self.task_mapping)] = [task, CLOUD_ID, FASTEST_CORE_GROUP,
                                                                 self.num_freqs[CLOUD_ID] - 1, is_mapped,
                                                                 self.instances[task]]

    def assignment(self):
        q = Queue()

        for source_task in self.source_tasks:
            q.put(source_task)

        while not q.empty():
            current_task = q.get()

            if not self.is_mapped(current_task):
                predecessors_mapping_info = self.get_predecessor_tasks_mapping_info(current_task)
                mapped_nodes = predecessors_mapping_info["Node"].tolist()
                mapped_tasks = predecessors_mapping_info["Task"].tolist()
                mapping_candidate_nodes = self.get_connected_nodes(mapped_nodes)
                mapping_candidate_nodes = self.get_sorted_mapping_candidate(mapping_candidate_nodes, mapped_nodes,
                                                                            mapped_tasks, current_task)
                is_assigned = False
                previous_mapping = self.task_mapping.loc[self.task_mapping["Task"] == current_task].iloc[0]
                for node in mapping_candidate_nodes:
                    if self.assign(node, FASTEST_CORE_GROUP, current_task, predecessors_mapping_info, -1):
                        self.unassign(previous_mapping["Node"], previous_mapping["Core Group"], current_task,
                                      pd.DataFrame(), -1)
                        self.task_mapping.loc[self.task_mapping["Task"] == current_task] = [current_task, node,
                                                                                            FASTEST_CORE_GROUP,
                                                                                            self.num_freqs[node] - 1,
                                                                                            True, self.instances[
                                                                                                current_task]]
                        self.active_nodes[node] = 1
                        is_assigned = True
                        break
                if not is_assigned:
                    self.task_mapping.loc[self.task_mapping["Task"] == current_task, "IsMapped"] = True

            successor_tasks = self.get_successor_tasks(current_task)
            for suc_tasks in successor_tasks:
                predecessors_mapping_info = self.get_predecessor_tasks_mapping_info(suc_tasks)
                if self.is_ready_to_map(predecessors_mapping_info):
                    q.put(suc_tasks)

        return True

    def tune_mapping(self):
        for j in range(len(self.task_mapping)):
            self.task_mapping.loc[j, "node type"] = self.get_node_type(self.task_mapping.iloc[j]["Node"])
            previous_mapping = self.task_mapping.iloc[j]
            current_core_group = previous_mapping["Core Group"]
            current_frequency = previous_mapping["Frequency"]
            selected_core_group = -1
            selected_frequency = -2
            is_tuned = False
            for core_group in range(self.num_groups[previous_mapping["Node"]], 0, -1):
                if not is_tuned:
                    self.unassign(previous_mapping["Node"], current_core_group, previous_mapping["Task"],
                                  pd.DataFrame(), current_frequency)
                    for k in range(self.num_freqs[previous_mapping["Node"]]):
                        if self.assign(previous_mapping["Node"], core_group, previous_mapping["Task"], pd.DataFrame(),
                                       k):
                            selected_core_group = core_group
                            selected_frequency = k
                            is_tuned = True
                            break
                else:
                    break

            self.task_mapping.loc[j, "Core Group"] = selected_core_group
            self.task_mapping.loc[j, "Frequency"] = selected_frequency

    def optimize(self):
        self.slacks_init()
        self.seeding()
        is_feasible = self.assignment()

        if not is_feasible:
            print("No Feasible Solution")
        else:
            self.tune_mapping()

    def generate_result(self, output_path):
        node_energy_consumption = pd.DataFrame(columns=["Node", "Base Power", "Communication", "Computation", "Overall"])
        overall_energy_consumption = pd.DataFrame(columns=["Base Power", "Communication", "Computation", "Overall"])
        edge_mapping = pd.DataFrame(columns=["source node", "source node type", "target node", "target node type", "source task", "source task name", "source task type", "target task", "target task name", "target task type"])

        base_energy_consumption = 0
        for i in range(sum(self.nodes)):
            node_base_energy_consumption = self.get_base_power(i) * self.deadline * self.active_nodes[i]
            node_energy_consumption.loc[i] = [i, node_base_energy_consumption, 0, 0, node_base_energy_consumption]
            base_energy_consumption += node_base_energy_consumption

        execution_energy_consumption = 0
        for i in range(len(self.task_mapping)):
            task = self.task_mapping.iloc[i]["Task"]
            task_execution_energy_consumption = self.get_task_energy(self.task_mapping.iloc[i]["Node"],
                                                                     self.cores[self.task_mapping.iloc[i]["Node"]],
                                                                     self.task_mapping.iloc[i]["Core Group"],
                                                                     self.workloads[task],
                                                                     self.max_widths[task],
                                                                     self.task_types[task],
                                                                     self.task_mapping.iloc[i]["Frequency"])

            node_energy_consumption.loc[node_energy_consumption["Node"] == self.task_mapping.iloc[i][
                "Node"], "Computation"] += task_execution_energy_consumption
            node_energy_consumption.loc[node_energy_consumption["Node"] == self.task_mapping.iloc[i][
                "Node"], "Overall"] += task_execution_energy_consumption
            execution_energy_consumption += task_execution_energy_consumption

        communication_energy_consumption = 0

        for r, s in self.edges:
            src_node = self.task_mapping.loc[self.task_mapping["Task"] == r].iloc[0]["Node"]
            dest_node = self.task_mapping.loc[self.task_mapping["Task"] == s].iloc[0]["Node"]

            edge_mapping.loc[len(edge_mapping)] = [src_node, self.get_node_type(src_node),
                                                   dest_node, self.get_node_type(dest_node),
                                                   r, self.task_names[r], self.task_types[r],
                                                   s, self.task_names[s], self.task_types[s]]

            if src_node != dest_node:
                task_communication_energy_consumption = self.get_comm_energy(src_node, dest_node,
                                                                             self.edge_weights[(r, s)])

                node_energy_consumption.loc[src_node, "Communication"] += task_communication_energy_consumption / 2
                node_energy_consumption.loc[src_node, "Overall"] += task_communication_energy_consumption / 2

                node_energy_consumption.loc[dest_node, "Communication"] += task_communication_energy_consumption / 2
                node_energy_consumption.loc[dest_node, "Overall"] += task_communication_energy_consumption / 2

                communication_energy_consumption += task_communication_energy_consumption

        total_energy_consumption = base_energy_consumption + execution_energy_consumption + communication_energy_consumption

        overall_energy_consumption.loc[0] = [base_energy_consumption, communication_energy_consumption,
                                             execution_energy_consumption, total_energy_consumption]
        print(total_energy_consumption)

        active_nodes_dict = {"solution_value": self.active_nodes}
        active_nodes_df = pd.DataFrame(active_nodes_dict)

        self.task_mapping.to_csv(output_path + "/tasks_allocation.csv")
        node_energy_consumption.to_csv(output_path + "/nodes_energy.csv")
        overall_energy_consumption.to_csv(output_path + "/consumed_energy.csv")
        active_nodes_df.to_csv(output_path + "/active_nodes.csv")
        edge_mapping.to_csv(output_path + "/edge_mapping.csv")
