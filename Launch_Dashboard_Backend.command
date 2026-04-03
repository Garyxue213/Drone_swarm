#!/bin/bash
# Move to the webots_swarm directory
cd "$(dirname "$0")/webots_swarm"

# Activate the virtual environment and install requirements
source venv/bin/activate
pip install -r requirements.txt

# Start the WebSocket telemetry backend
python3 swarm_web_backend.py
