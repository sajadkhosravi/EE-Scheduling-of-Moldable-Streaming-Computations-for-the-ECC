import pandas as pd
import random


def csv_to_chain_graphml(csv_files, graphml_file, data_transfer_lb, data_transfer_ub):
    # Define GraphML template
    graphml_template = """<?xml version="1.0" encoding="UTF-8"?>
    <graphml xmlns="http://graphml.graphdrawing.org/xmlns"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
             http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
    <!-- Created by igraph -->
      <key id="v_workload" for="node" attr.name="workload" attr.type="double"/>
      <key id="v_max_width" for="node" attr.name="max_width" attr.type="double"/>
      <key id="v_task_type" for="node" attr.name="task_type" attr.type="string"/>
      <key id="v_task_name" for="node" attr.name="task_name" attr.type="string"/>
      <key id="v_instance" for="node" attr.name="instance" attr.type="double"/>
      <key id="e_data_transfer" for="edge" attr.name="data_transfer" attr.type="double"/>
      <graph id="G" edgedefault="directed">
      </graph>
    </graphml>"""

    # Parse CSV and populate GraphML
    graphml_content = graphml_template

    dfs = []
    last_id = 0

    for csv_file in csv_files:
        dfs.append(pd.read_csv(csv_file))

    for df_index in range(len(dfs)):
        for row_index in range(len(dfs[df_index])):
            node_content = f"""<node id="n{last_id + dfs[df_index].loc[row_index, 'id']}">
                <data key="v_workload">{dfs[df_index].loc[row_index, 'workload']}</data>
                <data key="v_max_width">{dfs[df_index].loc[row_index, 'max_width']}</data>
                <data key="v_task_type">{dfs[df_index].loc[row_index, 'tasktype']}</data>
                <data key="v_task_name">task{dfs[df_index].loc[row_index, 'id']}</data>
                <data key="v_instance">{df_index}</data>
            </node>
            """
            graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)
        last_id += len(dfs[df_index])

    last_id = 0
    for df in dfs:
        for row_index in range(len(df) - 1):
            node_content = f"""<edge source="n{last_id + df.loc[row_index, 'id']}" target="n{last_id + df.loc[row_index + 1, 'id']}">
                <data key="e_data_transfer">{round(random.uniform(data_transfer_lb, data_transfer_ub), 4)}</data>
            </edge>
            """
            graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)
        last_id += len(df)

    with open(graphml_file, 'w') as output_file:
        output_file.write(graphml_content)

def csv_to_fully_parallel_graphml(csv_files, graphml_file, data_transfer_lb, data_transfer_ub):
    # Define GraphML template
    graphml_template = """<?xml version="1.0" encoding="UTF-8"?>
    <graphml xmlns="http://graphml.graphdrawing.org/xmlns"
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
             xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
             http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
    <!-- Created by igraph -->
      <key id="v_workload" for="node" attr.name="workload" attr.type="double"/>
      <key id="v_max_width" for="node" attr.name="max_width" attr.type="double"/>
      <key id="v_task_type" for="node" attr.name="task_type" attr.type="string"/>
      <key id="v_task_name" for="node" attr.name="task_name" attr.type="string"/>
      <key id="v_instance" for="node" attr.name="instance" attr.type="double"/>
      <key id="e_data_transfer" for="edge" attr.name="data_transfer" attr.type="double"/>
      <graph id="G" edgedefault="directed">
      </graph>
    </graphml>"""

    # Parse CSV and populate GraphML
    graphml_content = graphml_template

    dfs = []
    last_id = 0

    for csv_file in csv_files:
        dfs.append(pd.read_csv(csv_file))

    for df_index in range(len(dfs)):
        for row_index in range(len(dfs[df_index])):
            node_content = f"""<node id="n{last_id + dfs[df_index].loc[row_index, 'id']}">
                <data key="v_workload">{dfs[df_index].loc[row_index, 'workload']}</data>
                <data key="v_max_width">{dfs[df_index].loc[row_index, 'max_width']}</data>
                <data key="v_task_type">{dfs[df_index].loc[row_index, 'tasktype']}</data>
                <data key="v_task_name">task{dfs[df_index].loc[row_index, 'id']}</data>
                <data key="v_instance">{df_index}</data>
            </node>
            """
            graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)
        last_id += len(dfs[df_index])

    last_id = 0
    for df in dfs:
        for row_index in range(1, len(df) - 1):
            node_content = f"""<edge source="n{last_id + df.loc[0, 'id']}" target="n{last_id + df.loc[row_index, 'id']}">
                <data key="e_data_transfer">{round(random.uniform(data_transfer_lb, data_transfer_ub), 4)}</data>
            </edge>
            """
            graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)

        for row_index in range(1, len(df) - 1):
            node_content = f"""<edge source="n{last_id + df.loc[row_index, 'id']}" target="n{last_id + df.loc[len(df) - 1, 'id']}">
                <data key="e_data_transfer">{round(random.uniform(data_transfer_lb, data_transfer_ub), 4)}</data>
            </edge>
            """
            graphml_content = graphml_content.replace('</graph>', node_content + '</graph>', 1)

        last_id += len(df)

    with open(graphml_file, 'w') as output_file:
        output_file.write(graphml_content)

if __name__ == "__main__":

    number_of_tasks = 5
    number_of_task_sets = 12
    for j in range(0, 30):
        file_names = []
        for i in range(1, number_of_task_sets + 1):
            file_names.append("../../data/Workflows/RandomChain/generatedNodes/taskset_n"+str(number_of_tasks)+"_" + str((j * number_of_task_sets) + i) + ".csv")
        csv_to_chain_graphml(file_names, "../../data/Workflows/RandomChain/chain_"+str(number_of_tasks)+"_tasks_"+str(number_of_task_sets)+"_task_sets_random_graph_small_data_" + str(j) +".graphml", 1.0, 10.0)
        csv_to_chain_graphml(file_names, "../../data/Workflows/RandomChain/chain_"+str(number_of_tasks)+"_tasks_"+str(number_of_task_sets)+"_task_sets_random_graph_medium_data_" + str(j) +".graphml", 10.0, 20.0)
        csv_to_chain_graphml(file_names, "../../data/Workflows/RandomChain/chain_"+str(number_of_tasks)+"_tasks_"+str(number_of_task_sets)+"_task_sets_random_graph_large_data_" + str(j) +".graphml", 20.0, 30.0)
        csv_to_fully_parallel_graphml(file_names, "../../data/Workflows/RandomFullyParallel/fully_parallel_"+str(number_of_tasks)+"_tasks_"+str(number_of_task_sets)+"_task_sets_random_graph_small_data_" + str(j) +".graphml", 1.0, 10.0)
        csv_to_fully_parallel_graphml(file_names, "../../data/Workflows/RandomFullyParallel/fully_parallel_"+str(number_of_tasks)+"_tasks_"+str(number_of_task_sets)+"_task_sets_random_graph_medium_data_" + str(j) +".graphml", 10.0, 20.0)
        csv_to_fully_parallel_graphml(file_names, "../../data/Workflows/RandomFullyParallel/fully_parallel_"+str(number_of_tasks)+"_tasks_"+str(number_of_task_sets)+"_task_sets_random_graph_large_data_" + str(j) +".graphml", 20.0, 30.0)
