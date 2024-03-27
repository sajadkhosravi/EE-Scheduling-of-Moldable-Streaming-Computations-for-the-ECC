from ..optimizer import Optimizer
import gurobipy as grb


class RelaxedOptimizer(Optimizer):

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
        if self.get_node_type(orig_node) == 0 and self.get_node_type(dest_node) == 2:
            return (self.bandwidth_device_to_edge / 8) * deadline
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
        raise ValueError("Implausible node pair discovered in bandwidth request.")

    def get_node_download_links_volume(self, node, src_type):
        if self.get_node_type(node) == 1 and src_type == 0:
                # Volume depends on bandwidth and round length
                # Bandwidth is in MBit/s, deadline in s, volume in MB
            return (self.download_bandwidth_edge_device / 8) * self.deadline
        if self.get_node_type(node) == 2 and src_type == 1:
            return (self.download_bandwidth_cloud / 8) * self.deadline
        if self.get_node_type(node) == 1 and src_type == 1:
            return (self.download_bandwidth_edge_edge / 8) * self.deadline
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

    def optimize(self):
        num_nodes = sum(self.nodes)
        self.set_U = range(0, num_nodes)
        self.sets_I = [range(1, self.num_groups[u] + 1) for u in range(num_nodes)]
        self.set_J = range(0, self.num_tasks)
        self.sets_K = [range(0, self.num_freqs[u]) for u in range(num_nodes)]
        self.sets_M = [range(1, self.cores[u] + 1) for u in range(num_nodes)]

        # x_{u,i,j,k} = 1 if f task j runs in subgroup i of node u=(l,d) on frequency level k
        self.x_vars = {(u, i, j, k): self.opt_model.addVar(vtype=grb.GRB.BINARY, name="x_{0}_{1}_{2}_{3}".format(u, i, j, k)) for u in self.set_U for i in self.sets_I[u] for j in self.set_J for k in self.sets_K[u]}

        # y_{u,v,r,s} = 1 iff task graph edge (r,s) is mapped to network link (u,v)
        self.y_vars = {(u, v, r, s): self.opt_model.addVar(vtype=grb.GRB.BINARY, name="y_{0}_{1}_{2}_{3}".format(u, v, r, s)) for
                  u in self.set_U for v in self.set_U for r, s in self.edges}
        # z_u = 1 iff node u must be active, i.e. if at least one task is mapped to node u
        self.z_vars = {(u): self.opt_model.addVar(vtype=grb.GRB.BINARY, name="z_{0}".format(u)) for u in self.set_U}

        current_device = self.nodes[1] + self.nodes[2]
        for source_task in self.source_tasks:
            self.opt_model.addConstr(
                lhs=grb.quicksum(self.x_vars[current_device, i, source_task, k] for i in self.sets_I[current_device] for k in self.sets_K[current_device]),
                sense=grb.GRB.EQUAL,
                rhs=1,
                name="constraint_source_task_premapped_{0}".format(source_task)
            )
            current_device += 1
            if current_device >= num_nodes:
                current_device = self.nodes[1] + self.nodes[2]

        # Map all sink tasks to cloud
        for sink_task in self.sink_tasks:
            self.opt_model.addConstr(
                lhs=grb.quicksum(self.x_vars[0, i, sink_task, k] for i in self.sets_I[0] for k in self.sets_K[0]),
                sense=grb.GRB.EQUAL,
                rhs=1,
                name="constraint_sink_task_premapped_{0}".format(sink_task)
            )

        ################################################################
        # MODEL CONSTRAINTS
        ################################################################

        # Constraint: map each task to exactly one node, core group, and frequency level
        for j in self.set_J:
            self.opt_model.addConstr(
                lhs=grb.quicksum(self.x_vars[u, i, j, k] for u in self.set_U for i in self.sets_I[u] for k in self.sets_K[u]),
                sense=grb.GRB.EQUAL,
                rhs=1,
                name="constraint_mapped_once_{0}".format(j)
            )

        # Constraint: sum of task runtimes per core must not exceed deadline
        for u in self.set_U:
            for m in self.sets_M[u]:
                self.opt_model.addConstr(
                    lhs=grb.quicksum(
                        self.x_vars[u, i, j, k] * self.get_task_runtime(u, self.cores[u], i, self.workloads[j], self.max_widths[j], self.task_types[j], k) for i in self.get_groups(m, self.cores[u]) for j in self.set_J for k in self.sets_K[u]),
                    sense=grb.GRB.LESS_EQUAL,
                    rhs=self.deadline,
                    name="constraint_deadline_{0}_{1}".format(u, m)
                )

        # Constraint: force y_{u,v,r,s} to 1 if task graph edge (r,s) is mapped to network link (u,v)
        for u, v in self.network_links:
            for r, s in self.edges:
                self.opt_model.addConstr(
                    lhs=self.y_vars[u, v, r, s],
                    sense=grb.GRB.GREATER_EQUAL,
                    rhs=grb.quicksum(self.x_vars[u, i, r, k] for i in self.sets_I[u] for k in self.sets_K[u]) + grb.quicksum(
                        self.x_vars[v, idash, s, kdash] for idash in self.sets_I[v] for kdash in self.sets_K[v]) - 1,
                    name="constraint_edges_mapped_one_{0}_{1}_{2}_{3}".format(u, v, r, s)
                )

        # Constraint: every task graph edge must be mapped to network link or to node-local shared memory
        for r, s in self.edges:
            self.opt_model.addConstr(
                lhs=grb.quicksum(self.y_vars[u, v, r, s] for u, v in self.network_links) + grb.quicksum(self.y_vars[u, u, r, s] for u in self.set_U),
                sense=grb.GRB.EQUAL,
                rhs=1,
                name="constraint_all_edges_mapped_{0}_{1}".format(r, s)
            )

        # Constraint: network link bandwidth must not be exceeded
        # for u, v in self.network_links:
        #     self.opt_model.addConstr(
        #         lhs=grb.quicksum(self.y_vars[u, v, r, s] * self.edge_weights[(r, s)] for r, s in self.edges),
        #         sense=grb.GRB.LESS_EQUAL,
        #         rhs=self.get_link_volume(u, v, self.deadline),
        #         name="constraint_bandwidth_{0}_{1}".format(u, v)
        #     )

        for u in self.set_U:
            if self.get_node_type(u) == 0:
                self.opt_model.addConstr(
                        lhs=grb.quicksum(self.y_vars[u, v, r, s] * self.edge_weights[(r, s)] for v in self.set_U for r, s in self.edges if self.get_node_type(v) == 1 and (u, v) in self.network_links),
                        sense=grb.GRB.LESS_EQUAL,
                        rhs=self.get_node_upload_links_volume(u, 1),
                        name="constraint_upload_bandwidth_device_{0}".format(u)
                    )
            elif self.get_node_type(u) == 2:
                self.opt_model.addConstr(
                        lhs=grb.quicksum(self.y_vars[v, u, r, s] * self.edge_weights[(r, s)] for v in self.set_U for r, s in self.edges if self.get_node_type(v) == 1 and (v, u) in self.network_links),
                        sense=grb.GRB.LESS_EQUAL,
                        rhs=self.get_node_download_links_volume(u, 1),
                        name="constraint_download_bandwidth_cloud_{0}".format(u)
                    )
            elif self.get_node_type(u) == 1:
                self.opt_model.addConstr(
                        lhs=grb.quicksum(self.y_vars[v, u, r, s] * self.edge_weights[(r, s)] for r, s in self.edges for v in self.set_U if self.get_node_type(v) == 0 and (v, u) in self.network_links),
                        sense=grb.GRB.LESS_EQUAL,
                        rhs=self.get_node_download_links_volume(u, 0),
                        name="constraint_download_bandwidth_edge_{0}_from_device".format(u)
                    )
                self.opt_model.addConstr(
                    lhs=grb.quicksum(self.y_vars[v, u, r, s] * self.edge_weights[(r, s)] for r, s in self.edges for v in self.set_U if self.get_node_type(v) == 1 and v != u and (v, u) in self.network_links),
                    sense=grb.GRB.LESS_EQUAL,
                    rhs=self.get_node_download_links_volume(u, 1),
                    name="constraint_download_bandwidth_edge_{0}_from_edge".format(u)
                )
                self.opt_model.addConstr(
                    lhs=grb.quicksum(self.y_vars[u, v, r, s] * self.edge_weights[(r, s)] for r, s in self.edges for v in self.set_U if self.get_node_type(v) >= 1 and v != u and (u, v) in self.network_links),
                    sense=grb.GRB.LESS_EQUAL,
                    rhs=self.get_node_upload_links_volume(u, 1),
                    name="constraint_upload_bandwidth_edge_{0}".format(u)
                )
                # self.opt_model.addConstr(
                #     lhs=grb.quicksum(self.y_vars[u, v, r, s] * self.edge_weights[(r, s)] for r, s in self.edges for v in self.set_U if self.get_node_type(v) == 2 and (u, v) in self.network_links),
                #     sense=grb.GRB.LESS_EQUAL,
                #     rhs=self.get_node_upload_links_volume(u, 2),
                #     name="constraint_upload_bandwidth_edge_{0}_to_cloud".format(u)
                # )

        # Constraint: no backwards data flow
        for u in self.set_U:
            for v in self.set_U:
                if u != v and self.get_node_type(u) > self.get_node_type(v):
                    self.opt_model.addConstr(
                        lhs=grb.quicksum(self.y_vars[u, v, r, s] for r, s in self.edges),
                        sense=grb.GRB.EQUAL,
                        rhs=0,
                        name="constraint_backwards_dataflow_{0}_{1}".format(u, v)
                    )

                # Constraint: no data flow inside layers except edge layer
                if u != v and self.get_node_type(u) == self.get_node_type(v) and self.get_node_type(u) != 1:
                        self.opt_model.addConstr(
                            lhs=grb.quicksum(self.y_vars[u, v, r, s] for r, s in self.edges),
                            sense=grb.GRB.EQUAL,
                            rhs=0,
                            name="constraint_backwards_dataflow_{0}_{1}".format(u, v)
                        )
        # Constraint: node u must be active iff at least one task is mapped to it
        for u in self.set_U:
            for i in self.sets_I[u]:
                for j in self.set_J:
                    if self.workloads[j] > 0:
                        for k in self.sets_K[u]:
                            self.opt_model.addConstr(
                                lhs=self.z_vars[u],
                                sense=grb.GRB.GREATER_EQUAL,
                                rhs=self.x_vars[u, i, j, k],
                                name="constraint_active_one_{0}_{1}_{2}_{3}".format(u, i, j, k)
                            )
            self.opt_model.addConstr(
                lhs=self.z_vars[u],
                sense=grb.GRB.LESS_EQUAL,
                rhs=grb.quicksum(self.x_vars[u, i, j, k] for i in self.sets_I[u] for k in self.sets_K[u] for j in self.set_J if self.workloads[j] > 0),
                name="constraint_active_zero_{0}".format(u)
            )

        for r, s in self.edges:
            for u in self.set_U:
                for v in self.set_U:
                    if (u, v) not in self.network_links and u != v:
                        self.opt_model.addConstr(
                            lhs=grb.quicksum(self.x_vars[u, i, r, k] for i in self.sets_I[u] for k in self.sets_K[u]) + grb.quicksum(self.x_vars[v, idash, s, kdash] for idash in self.sets_I[v] for kdash in self.sets_K[v]),
                            sense=grb.GRB.LESS_EQUAL,
                            rhs=1,
                            name="constraint_no_edge_mapping_without_link_{0}_{1}_{2}_{3}".format(u, v, r, s)
                        )
                self.opt_model.addConstr(
                    lhs=grb.quicksum(self.x_vars[u, i, r, k] for i in self.sets_I[u] for k in self.sets_K[u]) + grb.quicksum(self.x_vars[u, idash, s, kdash] for idash in self.sets_I[u] for kdash in self.sets_K[u]) - 1,
                    sense=grb.GRB.LESS_EQUAL,
                    rhs=self.y_vars[u, u, r, s],
                    name="constraint_same_node_edge_mapping_{0}_{1}_{2}_{3}".format(u, u, r, s)
                )

        # Objective function: energy
        objective = grb.quicksum(self.get_base_power(u) * self.deadline * self.z_vars[u] for u in self.set_U) + grb.quicksum(self.get_task_energy(u, self.cores[u], i, self.workloads[j], self.max_widths[j], self.task_types[j], k) * self.x_vars[u, i, j, k] for u in self.set_U for i in self.sets_I[u] for j in self.set_J for k in self.sets_K[u]) + grb.quicksum(self.get_comm_energy(u, v, self.edge_weights[(r, s)]) * self.y_vars[u, v, r, s] for u, v in self.network_links for r, s in self.edges) + grb.quicksum(self.y_vars[u, v, r, s] * 100 for u in self.set_U for v in self.set_U for r, s in self.edges)

        self.opt_model.ModelSense = grb.GRB.MINIMIZE
        self.opt_model.setObjective(objective)

        self.opt_model.optimize()
