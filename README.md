# Energy-Efficient Scheduling of Moldable Streaming Computations for the Edge-Cloud Continuum


## Requirements
* Gurobi 11  
* Python 3.9 or above

## Running
```bash
pip install -r requirements.txt
python3 ./src/main.py <Strict|Relaxed|StrictHeuristic|RelaxedHeuristic>  <Small|Medium|Large> <input_file>  <output_path>
```

To install the necessary dependencies and run the script, use the following commands:

```bash
# Step 1: Install the required packages from the `requirements.txt` file
pip install -r requirements.txt

# Step 2: Execute the main script with the following arguments:
#   - METHOD: Select between Strict, Relaxed, StrictHeuristic, or RelaxedHeuristic
#   - ENV_SIZE: Choose between Small, Medium, or Large
#   - INPUT_FILE: Specify the path to the input file (/path/to/*.graphml)
#   - OUTPUT_PATH: Specify the directory where results should be saved

python3 ./src/main.py <METHOD> <ENV_SIZE> <INPUT_FILE> <OUTPUT_PATH>
```


## Reference
TBA