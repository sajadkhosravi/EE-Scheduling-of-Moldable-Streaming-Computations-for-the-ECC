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


if __name__ == "__main__":
    for j in range(0, 100):
        file_names = []
        for i in range(1, 12):
            file_names.append("../../data/Workflows/RandomChain/generatedNodes/taskset_n10_" + str((j * 12) + i) + ".csv")
        csv_to_chain_graphml(file_names, "../../data/Workflows/RandomChain/10_tasks_12_task_sets_random_graph_" + str(j) +".graphml", 10.0, 40.0)
