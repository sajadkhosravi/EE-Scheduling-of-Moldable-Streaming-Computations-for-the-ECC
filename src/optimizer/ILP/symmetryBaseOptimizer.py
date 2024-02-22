from .baseOptimizer import BaseOptimizer
import pandas as pd


class SymmetryBaseOptimizer(BaseOptimizer):

    def __init__(self, task_graph, compute_resource, network_info, execution_time_multipliers, power_info,
                 symmetry_level):
        super().__init__(task_graph, compute_resource, network_info, execution_time_multipliers, power_info)
        self.symmetry_level = symmetry_level

    def compute_deadline(self):
        cores = self.cores[0]
        total_workload = sum(self.workloads)
        # A7 is reference
        lower_bound = total_workload / (cores * self.freqs[0][len(self.freqs[0]) - 1])
        upper_target = total_workload / (cores * self.freqs[0][0])
        # self.deadline = (lower_bound + upper_target) / 2 / 25 * self.symmetry_level
        self.deadline = 2.857142857142857
        print("Deadline:", self.deadline)

    def data_completer(self, output_path):
        nodes_energy = pd.read_csv(output_path + "/nodes_energy.csv")
        nodes_energy_temp = pd.DataFrame(columns=["Node", "Computation", "Base Power", "Communication", "Overall"])
        overall_energy_arr = [0, 0, 0, 0]
        for i in range(self.nodes[2]):
            nodes_energy_temp.loc[i] = [i,
                                        nodes_energy.loc[i, "Computation"] * 2,
                                        nodes_energy.loc[i, "Base Power"],
                                        nodes_energy.loc[i, "Communication"] * 2,
                                        nodes_energy.loc[i, "Overall"] + nodes_energy.loc[i, "Computation"] +
                                        nodes_energy.loc[i, "Communication"]]
            overall_energy_arr[0] += nodes_energy_temp.loc[i, "Base Power"]
            overall_energy_arr[1] += nodes_energy_temp.loc[i, "Communication"]
            overall_energy_arr[2] += nodes_energy_temp.loc[i, "Computation"]
            overall_energy_arr[3] += nodes_energy_temp.loc[i, "Overall"]


        counter = self.nodes[2]
        for i in range(self.nodes[2], sum(self.nodes)):
            for j in range(self.symmetry_level - 1, -1, -1):
                nodes_energy_temp.loc[counter] = [self.symmetry_level * i - j,
                                                  nodes_energy.loc[i, "Computation"],
                                                  nodes_energy.loc[i, "Base Power"],
                                                  nodes_energy.loc[i, "Communication"],
                                                  nodes_energy.loc[i, "Overall"]]
                counter += 1

                overall_energy_arr[0] += nodes_energy.loc[i, "Base Power"]
                overall_energy_arr[1] += nodes_energy.loc[i, "Communication"]
                overall_energy_arr[2] += nodes_energy.loc[i, "Computation"]
                overall_energy_arr[3] += nodes_energy.loc[i, "Overall"]

        nodes_energy_temp["Node"] = nodes_energy_temp["Node"].astype('int')
        nodes_energy_temp.to_csv(output_path + "/nodes_energy.csv")

        overall_energy = pd.read_csv(output_path + "/consumed_energy.csv")

        overall_energy.loc[0] = overall_energy_arr

        overall_energy.to_csv(output_path + "/consumed_energy.csv")