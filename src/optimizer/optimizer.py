import math
import os
import pandas as pd
import gurobipy as grb

class Optimizer:

    def __init__(self, task_graph, compute_resource, network_info, execution_time_multipliers, power_info):
        #------------ Load Graph information -------------
        self.num_tasks = len(task_graph.vs)
        self.ids = [x for x in range(self.num_tasks)]
        self.workloads = [int(task_graph.vs[x]['workload']) for x in range(self.num_tasks)]
        self.max_widths = [int(task_graph.vs[x]['max_width']) for x in range(self.num_tasks)]
        self.task_types = [task_graph.vs[x]['task_type'] for x in range(self.num_tasks)]
        self.task_names = [task_graph.vs[x]['task_name'] for x in range(self.num_tasks)]
        self.instances = [int(task_graph.vs[x]['instance']) for x in range(self.num_tasks)]
        self.source_tasks = []
        self.sink_tasks = []
        for i in range(self.num_tasks):
            if not task_graph.predecessors(task_graph.vs[i]):
                self.source_tasks.append(i)
            if not task_graph.successors(task_graph.vs[i]):
                self.sink_tasks.append(i)
        self.edges = []
        self.edge_weights = {}
        for i in range(len(task_graph.es)):
            source = task_graph.es[i].source
            target = task_graph.es[i].target
            self.edges.append((source, target))
            # Edge weights are data transfers in MB
            self.edge_weights[(source, target)] = task_graph.es[i]['data_transfer']
        # =================================================

        # ------------ Load Nodes information -------------
        num_nodes = sum(compute_resource["nodes"])
        self.nodes = compute_resource["nodes"]
        self.freqs = compute_resource["frequencies"]
        self.network_links = network_info["network_links"]
        self.bandwidth_device_to_edge = network_info["bandwidth_device_to_edge"]
        self.power_device_to_edge = network_info["power_device_to_edge"]
        self.bandwidth_edge_to_cloud = network_info["bandwidth_edge_to_cloud"]
        self.power_edge_to_cloud = network_info["power_edge_to_cloud"]

        self.upload_bandwidth_device = network_info["upload_bandwidth_device"]
        self.download_bandwidth_edge_device = network_info["download_bandwidth_edge_device"]
        self.upload_bandwidth_edge_cloud = network_info["upload_bandwidth_edge_cloud"]
        self.download_bandwidth_cloud = network_info["download_bandwidth_cloud"]

        self.cores = compute_resource["num_cores"]
        self.num_groups = [self.cores[u] * 2 - 1 for u in range(num_nodes)]
        self.num_freqs = [len(self.freqs[2])] + [len(self.freqs[1])] * self.nodes[1] + [len(self.freqs[0])] * self.nodes[0]
        self.execution_time_multipliers = execution_time_multipliers
        self.powers = power_info["powers"]
        self.base_powers = power_info["base_powers"]
        # =================================================

        # ---------------- Load Optimizer -----------------
        self.opt_model = grb.Model(name="MIP Model")
        self.opt_model.setParam('TimeLimit', 10 * 60)
        # =================================================

        # ------------- Initialize Variables --------------
        self.set_U = []
        self.sets_I = []
        self.set_J = []
        self.sets_K = []
        self.sets_M = []
        self.x_vars = {}
        self.y_vars = {}
        self.z_vars = {}
        self.deadline = 0.0
        # =================================================

    def get_task_type_index(self, task_type):
        if task_type == 'MEMORY':
            return 0
        elif task_type == 'BRANCH':
            return 1
        elif task_type == 'FMULT':
            return 2
        elif task_type == 'SIMD':
            return 3
        elif task_type == 'MATMUL':
            return 4
        # DEFAULT is 5
        return 5

    # Returns list of proc's groups
    def get_groups(self, proc, procs):
        groups = []
        group = procs + proc - 1
        while group > 0:
            groups.append(group)
            group = group // 2
        groups.reverse()
        return groups

    # Node types are integers which serve as indices to the various information saved in lists
    # Node types are:
    # cloud: 2
    # edge: 1
    # device: 0
    def get_node_type(self, node):
        # Node 0 is cloud node
        if node == 0:
            return 2
        if node <= self.nodes[1]:
            return 1
        if node <= self.nodes[0] + self.nodes[1]:
            return 0
        raise ValueError("Invalid node ID encountered!")

    def get_node_type_string(self, node):
        # Node 0 is cloud node
        if node == 0:
            return "cloud"
        if node <= self.nodes[1]:
            return "edge"
        if node <= self.nodes[0] + self.nodes[1]:
            return "device"
        raise ValueError("Invalid node ID encountered!")

    # Computation of parallel efficiency as for Sanders Speck scheduler
    def par_eff(self, max_width, procs_alloc):
        R = 0.3
        if procs_alloc == 1:
            return 1.0
        if procs_alloc > 1 and procs_alloc <= max_width:
            return 1.0 - R * procs_alloc ** 2 / max_width ** 2
        return 0.000001

    # Returns width of group
    def get_group_width(self, group, procs):
        return procs / 2 ** math.floor(math.log(group, 2))

    def get_groups_with_specific_width(self, width, procs):
        if width > procs:
            return [1]
        pwr = math.floor(math.log(procs/width, 2))
        return [i for i in range(2**pwr, 2**(pwr + 1))]

    # Returns per-core runtime of task for given node, group, and core operating frequency
    def get_task_runtime(self, node, cores_on_node, group, workload, max_width, task_type, freq_lvl):
        node_type = self.get_node_type(node)
        freq = self.freqs[node_type][freq_lvl]
        ttind = self.get_task_type_index(task_type)
        procs_alloc = self.get_group_width(group, cores_on_node)
        return (workload * self.execution_time_multipliers[node_type][ttind]) / (
                    freq * procs_alloc * self.par_eff(max_width, procs_alloc))

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
        raise ValueError("Implausible node pair discovered in bandwidth request.")

    def get_base_power(self, node):
        node_type = self.get_node_type(node)
        return self.base_powers[node_type]

    # Total energy for task execution is computed from per-core runtime, power, and number of cores running the task
    def get_task_energy(self, node, cores_on_node, group, workload, max_width, task_type, freq_lvl):
        runtime = self.get_task_runtime(node, cores_on_node, group, workload, max_width, task_type, freq_lvl)
        node_type = self.get_node_type(node)
        ttind = self.get_task_type_index(task_type)
        return runtime * self.powers[node_type][ttind][freq_lvl] * self.get_group_width(group, cores_on_node)

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
            raise ValueError("Implausible node pair discovered in bandwidth request.")
        comm_duration = data_amount / (bandwidth / 8)
        # Communication energy is in J
        return comm_duration * power

    def compute_deadline(self):
        cores = self.cores[0]
        total_workload = sum(self.workloads)
        # A7 is reference
        lower_bound = total_workload / (cores * self.freqs[0][len(self.freqs[0]) - 1])
        upper_target = total_workload / (cores * self.freqs[0][0])
        self.deadline = (lower_bound + upper_target) / 2 / self.nodes[0]
        print("Deadline:", self.deadline)

    def get_node_upload_links_volume(self, node, dest_type):
        # Link exists, determine type of nodes
        if self.get_node_type(node) == 0 and dest_type == 1:
                # Volume depends on bandwidth and round length
                # Bandwidth is in MBit/s, deadline in s, volume in MB
            return (self.upload_bandwidth_device / 8) * self.deadline
        if self.get_node_type(node) == 1 and dest_type == 2:
            return (self.upload_bandwidth_edge_cloud / 8) * self.deadline
        return 0.0

    def get_node_download_links_volume(self, node, src_type):
        if self.get_node_type(node) == 1 and src_type == 0:
                # Volume depends on bandwidth and round length
                # Bandwidth is in MBit/s, deadline in s, volume in MB
            return (self.download_bandwidth_edge_device / 8) * self.deadline
        if self.get_node_type(node) == 2 and src_type == 1:
            return (self.download_bandwidth_cloud / 8) * self.deadline
        return 0.0

    def optimize(self):
        pass

    def generate_result(self, output_path):
        num_nodes = sum(self.nodes)
        if self.opt_model.SolCount >= 1:
            opt_df = pd.DataFrame.from_dict(self.x_vars, orient="index", columns=["variable_object"])
            opt_df.index = pd.MultiIndex.from_tuples(opt_df.index, names=["node", "group", "task", "frequency"])
            opt_df.reset_index(inplace=True)
            opt_df["solution_value"] = opt_df["variable_object"].apply(lambda item: item.X)
            opt_df.drop(columns=["variable_object"], inplace=True)
            opt_df.sort_values(by=["task"], inplace=True)

            opt_df_exp = opt_df[opt_df.solution_value > 0.5]

            # print(opt_df_exp)

            output_filename = "Distributed_crown_scheduling_alloction.csv"
            opt_df_exp.to_csv(output_path + "/" + output_filename, index=False,
                              columns=["node", "task", "group", "frequency"])

            y_df = pd.DataFrame.from_dict(self.y_vars, orient="index", columns=["variable_object"])
            y_df.index = pd.MultiIndex.from_tuples(y_df.index,
                                                   names=["link_source", "link_target", "edge_source", "edge_target"])
            y_df.reset_index(inplace=True)
            y_df["solution_value"] = y_df["variable_object"].apply(lambda item: item.X)
            y_df.drop(columns=["variable_object"], inplace=True)
            y_df_exp = y_df[y_df.solution_value > 0.5]
            # print(y_df_exp)

            z_df = pd.DataFrame.from_dict(self.z_vars, orient="index", columns=["variable_object"])
            z_df["solution_value"] = z_df["variable_object"].apply(lambda item: item.X)
            z_df.drop(columns=["variable_object"], inplace=True)
            # print(z_df)

            z_df.to_csv(output_path + "/active_nodes.csv")

            # print("Total tasks:", self.num_tasks)
            # print("Total tasks mapped:", len(opt_df_exp.index))
            # print("Total edges:", len(self.edges))
            # print("Total edges mapped:", len(y_df_exp.index))

            active_nodes = z_df['solution_value'].tolist()
            active_nodes = [int(i) for i in active_nodes]
            total_node_energy = 0.0
            nodes_idle_energies = [0.0] * num_nodes
            for i in range(len(active_nodes)):
                nodes_idle_energies[i] = self.get_base_power(i) * self.deadline * active_nodes[i]
                total_node_energy += nodes_idle_energies[i]
            # print("Total energy for keeping nodes active (base power):", total_node_energy)

            node_mapping = opt_df_exp['node'].tolist()
            group_mapping = opt_df_exp['group'].tolist()
            assigned_freqs = opt_df_exp['frequency'].tolist()
            total_task_energy = 0.0
            for i in range(self.num_tasks):
                total_task_energy += self.get_task_energy(node_mapping[i], self.cores[node_mapping[i]],
                                                          group_mapping[i],
                                                          self.workloads[i], self.max_widths[i], self.task_types[i],
                                                          assigned_freqs[i])
            # print("Total energy consumed for execution of tasks:", total_task_energy)

            comm_source_nodes = y_df_exp['link_source'].tolist()
            comm_target_nodes = y_df_exp['link_target'].tolist()
            comm_source_edges = y_df_exp['edge_source'].tolist()
            comm_target_edges = y_df_exp['edge_target'].tolist()
            total_comm_energy = 0.0
            comm_node_energies = [0.0] * num_nodes
            # print(comm_source_edges)
            for i in range(len(comm_source_nodes)):
                consumed_energy = self.get_comm_energy(comm_source_nodes[i], comm_target_nodes[i],
                                                       self.edge_weights[(comm_source_edges[i], comm_target_edges[i])])
                comm_node_energies[comm_source_nodes[i]] += consumed_energy / 2
                comm_node_energies[comm_target_nodes[i]] += consumed_energy / 2
                total_comm_energy += consumed_energy
            # print("Total energy consumed for communication:", total_commenergy)
            # print("Total energy consumed overall:", total_nodeenergy + total_taskenergy + total_commenergy)
            # print("Deadline (round length):", deadline)

            node_computational_energies = [0.0] * num_nodes
            task_energies = [0.0] * self.num_tasks
            for i in range(self.num_tasks):
                task_energy = self.get_task_energy(node_mapping[i], self.cores[node_mapping[i]], group_mapping[i],
                                                   self.workloads[i],
                                                   self.max_widths[i], self.task_types[i], assigned_freqs[i])
                node_computational_energies[node_mapping[i]] += task_energy
                task_energies[i] = task_energy

            # print("Node energies:")
            # for i in range(NUM_NODES):
            #     print("Node {}: {}".format(i, node_computational_energies[i]))

            node_energies = [0.0] * num_nodes
            for i in range(num_nodes):
                node_energies[i] = node_computational_energies[i] + nodes_idle_energies[i] + comm_node_energies[i]

            data = {
                "Node": range(len(node_computational_energies)),
                "Computation": node_computational_energies,
                "Base Power": nodes_idle_energies,
                "Communication": comm_node_energies,
                "Overall": node_energies
            }
            computational_energy_df = pd.DataFrame(data)
            computational_energy_df.to_csv(output_path + "/nodes_energy.csv")

            with open(output_path + "/consumed_energy.csv", 'w') as dcs:
                dcs.write("Base Power,Communication,Computation,Overall\n")
                dcs.write("{},{},{},{}\n".format(total_node_energy, total_comm_energy, total_task_energy,
                                                 total_node_energy + total_task_energy + total_comm_energy))

            #
            # with open(output_path + "/nodes_energy.csv", 'w') as dcs:
            #     dcs.write("node,energy\n")
            #     for i in range(NUM_NODES):
            #         dcs.write("{},{}\n".format(i, node_energies[i]))

            with open(output_path + "/distr_crown_sched.csv", 'w') as dcs:
                dcs.write("node,node type,instance,task,task name,task type,group,frequency level,task energy\n")
                for i in range(self.num_tasks):
                    dcs.write(
                        "{},{},{},{},{},{},{},{}\n".format(node_mapping[i], self.get_node_type_string(node_mapping[i]),
                                                           self.instances[i], i, self.task_names[i], self.task_types[i],
                                                           group_mapping[i], assigned_freqs[i], task_energies[i]))

            with open(output_path + "/distr_crown_edge_mapping.csv", 'w') as emf:
                emf.write(
                    "source node,source node type,target node,target node type,source task,source task name,source task type,target task,target task name,target task type\n")
                for i in range(len(comm_source_nodes)):
                    emf.write("{},{},{},{},{},{},{},{},{},{}\n".format(comm_source_nodes[i],
                                                                       self.get_node_type_string(comm_source_nodes[i]),
                                                                       comm_target_nodes[i],
                                                                       self.get_node_type_string(comm_target_nodes[i]),
                                                                       comm_source_edges[i],
                                                                       self.task_names[comm_source_edges[i]],
                                                                       self.task_types[comm_source_edges[i]],
                                                                       comm_target_edges[i],
                                                                       self.task_names[comm_target_edges[i]],
                                                                       self.task_types[comm_target_edges[i]]))

            # print("Constraint slack values for edge mapping:")
            # for u,v in NETWORK_LINKS:
            #     for r,s in taskgraph_edges:
            #         if r ==0 and s==3:
            #             slack = opt_model.getConstrByName("constraint_edges_mapped_one_{0}_{1}_{2}_{3}".format(u,v,r,s)).Slack
            #             print("({},{},{},{}): {}".format(u,v,r,s,slack))

            with open(output_path + "/energy_distr_crown.csv", 'a+') as energyfile:
                if os.path.getsize(output_path + "/energy_distr_crown.csv") == 0:
                    energyfile.write("taskset,energy_consumption\n")
                energyfile.write(os.path.splitext(output_path)[0] + "," + str(self.opt_model.objVal) + "\n")

            # print('Obj: %g' % self.opt_model.objVal)
        else:
            print("No feasible solution found!")
            with open(output_path + "/energy_distr_crown.csv", 'a') as energyfile:
                if os.path.getsize(output_path + "/energy_distr_crown.csv") == 0:
                    energyfile.write("taskset,energy_consumption\n")
                energyfile.write(os.path.splitext(output_path)[0] + "," + "\n")
        with open(output_path + "/optstat_distr_crown.csv", 'a') as optstatfile:
            if os.path.getsize(output_path + "/optstat_distr_crown.csv") == 0:
                optstatfile.write("taskset,optimization status,MIPGap\n")
            optstatfile.write(
                os.path.splitext(output_path)[0] + "," + str(self.opt_model.Status) + "," + str(
                    self.opt_model.MIPGap) + "\n")
