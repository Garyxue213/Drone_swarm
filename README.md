# 🛸 Drone Swarm Search & Rescue (SAR) Logic Viz

This repository contains the logic implementation and algorithm specifications for our university group's Drone Swarm Search & Rescue assignment. It specifically features an interactive 2D graphical visualization of the swarm's logic, demonstrating autonomous coordination, dynamic task re-allocation, and resilience against communication jamming or hardware failure.

## 🚀 How to Run the 2D Visualization (Python)

To see a real-time, top-down visualization of our swarm's "Dynamic Sectoring" logic in action:

1. Clone this repository.
2. Install dependencies (Requires `matplotlib` and `numpy`).
3. Run the visualization script from your terminal:
   ```bash
   cd webots_swarm
   python3 swarm_2d_sim.py
   ```
*(Or simply double click on `Launch_2D_Logic_Viz.command` if you are on macOS!)*

---

## ⌨️ Interactive Controls
While the 2D map is running, use these keyboard controls to demonstrate our logic fail-safes to graders:

*   **[P] Change Flight Pattern:** Swaps the swarm's mathematical search tracking structure between "Vertical Sweep", "Zig-Zag", and "Circular Patrol", which instantly scale to conform to the dimensions of each drone's assigned sector.
*   **[B] Battery Drain:** Instantly plunges Drone 1's (Alpha) battery to < 15%, triggering the "Return to Base" fail-safe and dynamically expanding the remaining drones' search sectors to compensate for the gap.
*   **[H] Hide Target:** Toggles the search target on/off. Hiding the target allows the swarm to demonstrate 100% map coverage and continuous scanning behaviors.
*   **[R] Restart:** Instantly resets the simulation simulation and state arrays back to T=0s.

---

## 🧠 Swarm Technology & Scenario
### 1. Dynamic Sectoring Failovers
The swarm maintains a simulated "Shared Vitality Table" mimicking a low-bandwidth mesh network emitting heartbeats. 
- **Normal Ops:** The search map is divided evenly among 3 drones.
- **Jamming Attack:** At T=15s, Drone 3 simulated a complete catastrophic communication loss (a "Jamming" attack).
- **Graceful Recovery:** The remaining drones continuously calculate active numbers. The loss stretches their search strips perfectly mathematically to prevent any gaps in real time.

### 2. Full Research Write-Up
Please refer to `answers.md` in the root folder for our full university report detailing the 6-Step Rule-Based Swarm Algorithm execution process.
