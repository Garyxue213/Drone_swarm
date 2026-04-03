# Drone Swarm Construction Mapping & 3D Surveying

Welcome to the **Drone Swarm Construction Mapping** visualizer. This repository contains the Python-based logic simulation for an IoT mesh-network of drones conducting industrial surveying, photogrammetry scanning, and dynamic obstacle avoidance.

## Project Scope
This project pivots away from basic search and rescue to address modern industrial capabilities: **Digital Twins** and **Site Safety**. The drone swarm dynamically tracks topographical elevations (Z-Axis), executes Orthomosaic patterns, and features a self-healing algorithm where surviving drones will expand their search footprint if a teammate suffers hardware malfunction or battery depletion.

## How to Run the Visualizers
We offer two distinct ways to run the algorithm:

### 1. Google Earth KML Export 🌍 (High Realism)
To view the simulation mapped directly over real-world satellite imagery and 3D terrain:
1. Run `pip install simplekml`
2. Run `python3 webots_swarm/generate_kml.py`
3. A `drone_survey.kml` file will be generated in your root directory.
4. Drag and drop this `.kml` file into [Google Earth Web](https://earth.google.com/) or double-click to open in Google Earth Pro. You will see the entire flight survey!

### 2. Python 3D Logic Visualizer (UI)
The AI logic is also visualized through an interactive Python 3D simulation featuring live POV target cameras.

**Requirements**: You must have `matplotlib` and `numpy` installed.
```bash
pip install matplotlib numpy
```

**Launch**:
```bash
python3 webots_swarm/swarm_3d_sim.py
```

### 3. Digital Twin Dashboard (Web UI) 🖥️
The project also features a modern, high-performance web dashboard to monitor live drone telemetry.

**Requirements**: You must have **Python 3** and **Node.js / NPM** installed on your machine.

**Launch**:
1. Double-click **`Launch_Dashboard_Backend.command`** — starts the Python WebSocket telemetry server.
2. Double-click **`Launch_Dashboard_Frontend.command`** — starts the web UI.
3. Open **`http://localhost:5173`** in your browser.

The dashboard will automatically connect to the backend. The **"LIVE TELEMETRY"** indicator will turn green once data is streaming!

## Interactive Testing Controls (Keyboard HUD)
While the simulation runs, you can trigger events to test the swarm's real-time dynamic pathing:

*   **`[P]` - Toggle Flight Pattern**: Instantly commands the swarm to switch between *Orthomosaic Grid*, *Topographical Zig-Zag*, or *Circular Scan*.
*   **`[C]` - Spawn Crane Obstacle**: Spawns a sudden 150m-tall Crane object directly in the path of D1, demonstrating the drone's logic for calculating high-elevation clearance.
*   **`[B]` - Force Battery Shutdown**: Instantly drops Drone 1 (Alpha) to Critical Battery (14.9%), triggering an Emergency Landing / RTB. Watch the remaining drones dynamically resize their sector-widths to guarantee 100% map coverage!
*   **`[R]` - Restart Verification**: Wipes the building structures, resets the drones, and clears the area-scanned progress.
