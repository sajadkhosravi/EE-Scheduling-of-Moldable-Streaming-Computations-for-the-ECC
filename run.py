import subprocess

for i in range(10, 100):
  subprocess.run("mkdir .\\output\\Base\\Random" + str(i), shell=True, check=True)
  command_template = "python ./src/main.py Base ./data/Workflows/RandomChain/10_tasks_12_task_sets_random_graph_"+str(i)+".graphml .\\output\\Base\\Random" + str(i)
  try:
    # Execute the command using subprocess
    subprocess.run(command_template, shell=True, check=True)
  except subprocess.CalledProcessError as e:
    print(f"Error running command: {e}")

print("Commands executed successfully.")