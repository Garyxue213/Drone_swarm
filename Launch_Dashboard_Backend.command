#!/bin/bash
# Automatically change to the backend directory, no matter where this is run from
cd "$(dirname "$0")/webots_swarm"

# Install requirements and run
pip3 install websockets
python3 swarm_web_backend.py
