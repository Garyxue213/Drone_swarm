# Drone Swarm Construction Mapping & 3D Surveying

Welcome to the **Drone Swarm Construction Mapping** visualizer. This repository contains the Python-based logic simulation for an IoT mesh-network of drones conducting industrial surveying, photogrammetry scanning, and dynamic obstacle avoidance.

## Project Scope
This project pivots away from basic search and rescue to address modern industrial capabilities: **Digital Twins** and **Site Safety**. The drone swarm dynamically tracks topographical elevations (Z-Axis), executes Orthomosaic patterns, and features a self-healing algorithm where surviving drones will expand their search footprint if a teammate suffers hardware malfunction or battery depletion.

## How to Run the Logic Visualizer
The AI logic and simulation is visualized entirely through a Python 3D Topographical Map.

**Requirements**: You must have `matplotlib` and `numpy` installed.
```bash
pip install matplotlib numpy
```

**Launch**:
```bash
python3 webots_swarm/swarm_3d_sim.py
```
*(Or simply run the included `Launch_3D_Logic_Viz.command` file on Mac/Linux).*

## Interactive Testing Controls (Keyboard HUD)
While the simulation runs, you can trigger events to test the swarm's real-time dynamic pathing:

*   **`[P]` - Toggle Flight Pattern**: Instantly commands the swarm to switch between *Orthomosaic Grid*, *Topographical Zig-Zag*, or *Circular Scan*.
*   **`[C]` - Spawn Crane Obstacle**: Spawns a sudden 150m-tall Crane object directly in the path of D1, demonstrating the drone's logic for calculating high-elevation clearance.
*   **`[B]` - Force Battery Shutdown**: Instantly drops Drone 1 (Alpha) to Critical Battery (14.9%), triggering an Emergency Landing / RTB. Watch the remaining drones dynamically resize their sector-widths to guarantee 100% map coverage!
*   **`[R]` - Restart Verification**: Wipes the building structures, resets the drones, and clears the area-scanned progress.
