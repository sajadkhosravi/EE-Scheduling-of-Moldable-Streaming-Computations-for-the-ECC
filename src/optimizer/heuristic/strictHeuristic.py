from ..optimizer import Optimizer
from queue import Queue

import pandas as pd

CLOUD_ID = 0


class Heuristic(Optimizer):
    def __init__(self, task_graph, compute_resource, network_info, execution_time_multipliers, power_info):
        super().__init__(task_graph, compute_resource, network_info, execution_time_multipliers, power_info)
        self.workload_slack = []
        self.outgoing_channel_slack = []
        self.incoming_channel_slack = []
        self.active_nodes = [0] * sum(self.nodes)
        self.active_nodes[CLOUD_ID] = 1
        self.task_mapping = pd.DataFrame(columns=["Task", "Node", "Core Group", "Frequency", "IsMapped", "Instance"])

    def get_node_available_upload_links_volume(self, node, dest_type):
        return self.outgoing_channel_slack[node][dest_type]

    def get_node_available_download_links_volume(self, node, src_type):
        return self.incoming_channel_slack[node][src_type]

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
        else:
            return float("inf")
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
        for u in predecessor_nodes:
            if u not in common_nodes_arr:
                common_nodes_arr.append(u)
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

    def is_ready_to_map(self, task, predecessors_mapping_info):
        predecessors = self.get_predecessor_tasks(task)
        return len(predecessors) == len(predecessors_mapping_info)

    def is_mapped(self, task):
        mapping_info = self.task_mapping[self.task_mapping["Task"] == task]
        return len(mapping_info) > 0 and mapping_info.iloc[0]["IsMapped"]

    def get_core_groups_sorted(self, node, max_width):
        needed_cores = max_width
        core_groups = self.get_groups_with_specific_width(needed_cores, self.cores[node])
        while len(core_groups) == 0:
            needed_cores /= 2
            core_groups = self.get_groups_with_specific_width(needed_cores, self.cores[node])
        data = {}
        for group in core_groups:
            data[group] = self.workload_slack[node][group - 1]
        return sorted(data, key=lambda x: data[x], reverse=True)

    def is_assignable(self, node, core_group, task, predecessors_info, required_time, outgoing_channel_slack,
                      incoming_channel_slack, workload_slack):
        workload_assignment_status = True
        channel_assignment_status = True

        for i in range(len(predecessors_info)):
            if node == predecessors_info.iloc[i]["Node"]:
                continue
            remained_outgoing_channel_volume = outgoing_channel_slack[predecessors_info.iloc[i]["Node"]][self.get_node_type(node)] - \
                                             self.edge_weights[(predecessors_info.iloc[i]["Task"], task)]
            remained_incoming_channel_volume = incoming_channel_slack[node][self.get_node_type(predecessors_info.iloc[i]["Node"])] - self.edge_weights[
                (predecessors_info.iloc[i]["Task"], task)]

            if remained_outgoing_channel_volume < 0 or remained_incoming_channel_volume < 0:
                channel_assignment_status = False
                break
            outgoing_channel_slack[predecessors_info.iloc[i]["Node"]][self.get_node_type(node)] = remained_outgoing_channel_volume
            incoming_channel_slack[node][self.get_node_type(predecessors_info.iloc[i]["Node"])] = remained_incoming_channel_volume

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

    def assign(self, node, core_group, task, predecessors_info, frequency_level):
        temp_upload_channel_slack = self.outgoing_channel_slack.copy()
        temp_download_channel_slack = self.incoming_channel_slack.copy()
        temp_workload_slack = self.workload_slack[node].copy()

        required_time = self.get_task_runtime(node, self.cores[node], core_group, self.workloads[task],
                                              self.max_widths[task], self.task_types[task], frequency_level)

        workload_status, channel_status = self.is_assignable(node, core_group, task, predecessors_info, required_time,
                                                             temp_upload_channel_slack, temp_download_channel_slack,
                                                             temp_workload_slack)
        if workload_status and channel_status:
            self.workload_slack[node] = temp_workload_slack
            self.outgoing_channel_slack = temp_upload_channel_slack
            self.incoming_channel_slack = temp_download_channel_slack
            return True

        return False

    def unassign(self, node, core_group, task, frequency_level):
        required_time = self.get_task_runtime(node, self.cores[node], core_group, self.workloads[task],
                                              self.max_widths[task], self.task_types[task], frequency_level)

        core_groups = [core_group]
        core_groups = core_groups + self.get_parent_core_groups(core_group)
        core_groups = core_groups + self.get_child_core_groups(core_group, self.num_groups[node])
        for i in core_groups:
            self.workload_slack[node][i - 1] = self.workload_slack[node][i - 1] + required_time

    def get_total_task_energy(self, src_nodes, dest_node, src_tasks, dest_task, core_group):
        execution_energy = self.get_task_energy(dest_node, self.cores[dest_node], core_group,self.workloads[dest_task],
                                                self.max_widths[dest_task], self.task_types[dest_task], -1)

        comm_energy = 0
        for i in range(len(src_nodes)):
            comm_energy += self.get_comm_energy(src_nodes[i], dest_node, self.edge_weights[(src_tasks[i], dest_task)])

        total_energy = execution_energy + comm_energy
        if self.active_nodes[dest_node] == 0:
            total_energy += self.get_base_power(dest_node) * self.deadline

        return total_energy

    def get_sorted_mapping_candidate(self, available_nodes, src_nodes, src_tasks, dest_task):
        candidates = {}
        for node in available_nodes:
            candidates[node] = self.get_total_task_energy(src_nodes, node, src_tasks, dest_task)

        return sorted(candidates, key=lambda x: candidates[x])

    def get_sorted_mapping_candidate_by_energy_and_workload(self, available_nodes, src_nodes, src_tasks, dest_task):
        candidates = {}
        max_energy = 0
        max_workload = 0
        for node in available_nodes:
            core_groups = self.get_core_groups_sorted(node, self.max_widths[dest_task])
            candidates[node] = {"energy": self.get_total_task_energy(src_nodes, node, src_tasks, dest_task, core_groups[0]), "available_workload": self.workload_slack[node][core_groups[0] - 1]}
            if candidates[node]["energy"] > max_energy:
                max_energy = candidates[node]["energy"]
            if candidates[node]["available_workload"] > max_workload:
                max_workload = candidates[node]["available_workload"]

        for node in available_nodes:
            energy_norm = 0
            available_workload_norm = 0
            if max_energy > 0:
                energy_norm = candidates[node]["energy"] / max_energy
            if max_workload > 0:
                available_workload_norm = candidates[node]["available_workload"] / max_workload
            candidates[node] = energy_norm + available_workload_norm
        return sorted(candidates, key=lambda x: candidates[x])

    def slacks_init(self):
        # Initialize channel slack vector
        for u in range(sum(self.nodes)):
            self.outgoing_channel_slack.append(
                [
                    self.get_node_outgoing_links_volume(u, 0),
                    self.get_node_outgoing_links_volume(u, 1),
                    self.get_node_outgoing_links_volume(u, 2),
                ]
            )
            self.incoming_channel_slack.append(
                [
                    self.get_node_incoming_links_volume(u, 0),
                    self.get_node_incoming_links_volume(u, 1),
                    self.get_node_incoming_links_volume(u, 2),
                ]
            )

        # Initialize workload slack vector
        for layer in range(2, -1, -1):
            for i in range(self.nodes[layer]):
                index = i
                for j in range(2, layer, -1):
                    index = index + self.nodes[j]
                workload_time_array = [self.deadline] * self.num_groups[index]
                self.workload_slack.append(workload_time_array)

    def seeding(self):
        current_device = self.nodes[1] + self.nodes[2]
        num_nodes = sum(self.nodes)

        for task in self.source_tasks:
            core_groups = self.get_core_groups_sorted(current_device, self.max_widths[task])
            if self.assign(current_device, core_groups[0], task, pd.DataFrame(), -1):
                self.task_mapping.loc[len(self.task_mapping)] = [task, current_device, core_groups[0],
                                                                 self.num_freqs[current_device] - 1, True,
                                                                 self.instances[task]]
                self.active_nodes[current_device] = 1
                current_device += 1
                if current_device >= num_nodes:
                    current_device = self.nodes[1] + self.nodes[2]
            else:
                return False

        for task in self.sink_tasks:
            core_groups = self.get_core_groups_sorted(CLOUD_ID, self.max_widths[task])
            if self.assign(CLOUD_ID, core_groups[0], task, pd.DataFrame(), -1):
                self.task_mapping.loc[len(self.task_mapping)] = [task, CLOUD_ID, core_groups[0],
                                                                 self.num_freqs[CLOUD_ID] - 1, True,
                                                                 self.instances[task]]
            else:
                return False

        return True

    def remove_infeasible_candidates(self, task, mapping_candidates, pred_nodes, pred_tasks):
        feasible_candidates = []
        successor_tasks = self.get_successor_tasks(task)
        sink_successors = [t for t in successor_tasks if t in self.sink_tasks]
        only_edge = False
        if len(sink_successors) > 0:
            only_edge = True
        for mapping_candidate_in_layer in mapping_candidates:
            for candidate in mapping_candidate_in_layer:
                candidate_type = self.get_node_type(candidate)
                if only_edge and candidate_type == 0:
                    continue
                for i in range(len(pred_nodes)):
                    if candidate == pred_nodes[i]:
                        continue
                    if self.get_node_available_upload_links_volume(pred_nodes[i], candidate_type) < self.edge_weights[(pred_tasks[i], task)]:
                        break
                    if self.get_node_available_download_links_volume(candidate, self.get_node_type(pred_nodes[i])) < \
                            self.edge_weights[(pred_tasks[i], task)]:
                        break

                feasible_candidates.append(candidate)
        return feasible_candidates

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
                feasible_candidates = self.remove_infeasible_candidates(current_task, mapping_candidate_nodes,
                                                                        mapped_nodes, mapped_tasks)
                # mapping_candidate_nodes = self.get_sorted_mapping_candidate(feasible_candidates, mapped_nodes, mapped_tasks, current_task)
                mapping_candidate_nodes = self.get_sorted_mapping_candidate_by_energy_and_workload(feasible_candidates,
                                                                                                   mapped_nodes,
                                                                                                   mapped_tasks,
                                                                                                   current_task)
                is_assigned = False
                for node in mapping_candidate_nodes:
                    core_groups = self.get_core_groups_sorted(node, self.max_widths[current_task])
                    for i in core_groups:
                        if self.assign(node, i, current_task, predecessors_mapping_info, -1):
                            self.task_mapping.loc[len(self.task_mapping)] = [current_task, node, i, self.num_freqs[node] - 1, True, self.instances[current_task]]
                            self.active_nodes[node] = 1
                            is_assigned = True
                            break
                    if is_assigned:
                        break
                if not is_assigned:
                    return False

            successor_tasks = self.get_successor_tasks(current_task)
            for suc_tasks in successor_tasks:
                predecessors_mapping_info = self.get_predecessor_tasks_mapping_info(suc_tasks)
                if self.is_ready_to_map(suc_tasks, predecessors_mapping_info):
                    q.put(suc_tasks)

        return True

    def get_required_energy_on_different_groups_and_frequencies(self, node, task):
        required_energy = {}
        for i in range(1, self.num_groups[node] + 1):
            for k in range(self.num_freqs[node]):
                required_energy[str(i) + "-" + str(k)] = self.get_task_energy(node, self.cores[node], i,
                                                                              self.workloads[task],
                                                                              self.max_widths[task],
                                                                              self.task_types[task], k)
        return sorted(required_energy, key=lambda x: required_energy[x])

    def tune_mapping(self):
        for j in range(len(self.task_mapping)):
            self.task_mapping.loc[j, "node type"] = self.get_node_type(self.task_mapping.iloc[j]["Node"])
            previous_mapping = self.task_mapping.iloc[j]
            current_core_group = previous_mapping["Core Group"]
            current_frequency = previous_mapping["Frequency"]
            selected_core_group = -1
            selected_frequency = -2

            sorted_group_frequency_list = self.get_required_energy_on_different_groups_and_frequencies(
                previous_mapping["Node"], previous_mapping["Task"])

            self.unassign(previous_mapping["Node"], current_core_group, previous_mapping["Task"], current_frequency)
            for ik in sorted_group_frequency_list:
                ik_arr = ik.split("-")
                if self.assign(previous_mapping["Node"], int(ik_arr[0]), previous_mapping["Task"], pd.DataFrame(),
                               int(ik_arr[1])):
                    selected_core_group = int(ik_arr[0])
                    selected_frequency = int(ik_arr[1])
                    break

            self.task_mapping.loc[j, "Core Group"] = selected_core_group
            self.task_mapping.loc[j, "Frequency"] = selected_frequency

    def optimize(self):
        if self.num_tasks < 3:
            print("No Feasible Solution")
            return -1

        self.slacks_init()

        is_feasible = self.seeding()

        if not is_feasible:
            print("No Feasible Solution")
        else:
            is_feasible = self.assignment()

            if not is_feasible:
                print("No Feasible Solution")
            else:
                self.tune_mapping()
                return 1

        return -1

    def generate_result(self, output_path):
        node_energy_consumption = pd.DataFrame(
            columns=["Node", "Base Power", "Communication", "Computation", "Overall"])
        overall_energy_consumption = pd.DataFrame(columns=["Base Power", "Communication", "Computation", "Overall"])
        edge_mapping = pd.DataFrame(
            columns=["source node", "source node type", "target node", "target node type", "source task",
                     "source task name", "source task type", "target task", "target task name", "target task type"])

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

        return 1
