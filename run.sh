#!/bin/bash

source venv/bin/activate

pip install -r requirements.txt

mkdir output
mkdir output/Base
mkdir output/Relaxed
mkdir output/SymmetryBase
mkdir output/SymmetryRelaxed



python3 ./src/main.py Base ../Data/Workflows/SDE/hautalatg_4_ewmod.graphml ../output/Base
python3 ./src/main.py Relaxed ../Data/Workflows/SDE/hautalatg_4_ewmod.graphml ../output/Relaxed
python3 ./src/main.py SymmetryBase ../Data/Workflows/SDE/hautalatg_4_ewmod.graphml ../output/SymmetryBase
python3 ./src/main.py SymmetryRelaxed ../Data/Workflows/SDE/hautalatg_4_ewmod.graphml ../output/SymmetryRelaxed