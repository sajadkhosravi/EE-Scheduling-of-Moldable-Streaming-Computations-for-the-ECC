from .relaxedOptimizer import RelaxedOptimizer


class SymmetryRelaxedOptimizer(RelaxedOptimizer):

    def __init__(self, task_graph, compute_resource, network_info, execution_time_multipliers, power_info, symmetry_level):
        super().__init__(task_graph, compute_resource, network_info, execution_time_multipliers, power_info)
        self.symmetry_level = symmetry_level

    def compute_deadline(self):
        cores = self.cores[0]
        total_workload = sum(self.workloads)
        # A7 is reference
        lower_bound = total_workload / (cores * self.freqs[0][len(self.freqs[0]) - 1])
        upper_target = total_workload / (cores * self.freqs[0][0])
        self.deadline = (lower_bound + upper_target) / 2 / 25 * self.symmetry_level
        print("Deadline:", self.deadline)