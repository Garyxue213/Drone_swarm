#!/bin/bash
# Move to the project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Run the 2D simulation
python3 swarm_3d_sim.py
