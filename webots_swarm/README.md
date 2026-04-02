# 🛸 Webots Drone Swarm Search & Rescue (SAR)

This project implements a rule-based drone swarm simulation for a university Search and Rescue assignment. It demonstrates autonomous coordination, dynamic sectoring, and resilience against communication jamming or hardware failure.

## 🚀 One-Click Launch
Double-click the launcher on your desktop:
**`Launch_Swarm_Sim.command`**

*(Or run `webots_swarm/worlds/swarm_mission.wbt` directly in Webots)*

### 📊 2D Visualization (Python)
To see a simplified, top-down view of the "Dynamic Sectoring" logic, run the launcher on your desktop:
**`Launch_2D_Logic_Viz.command`**

*(Or run `source venv/bin/activate && python3 webots_swarm/swarm_2d_sim.py`)*

---

## 🧠 Swarm Technology
### 1. Dynamic Sectoring Algorithm
The swarm maintains a "Shared Vitality Table" via a low-bandwidth mesh network (heartbeats). 
- **Normal Ops:** The search area is divided equally among 3 drones.
- **Failover:** If a drone stops sending heartbeats (simulating jamming or a crash), the remaining drones instantly detect the loss and stretch their search sectors to cover the gap.

### 2. Rule-Based Control
- **No Heavy ML:** Uses standard PID controllers for flight stability.
- **Mesh Networking:** Simple string-based packet exchange via Webots Emitters/Receivers.
- **Autonomous Recovery:** Logic is decentralized; each drone calculates its own target based on who else is currently alive.

---

## 🛡️ Cybersecurity Focus
The simulation includes a **Simulated Jamming Attack**:
- At **T:45 seconds**, Drone 3 (Right Sector) is "jammed" and stops communicating.
- View the Webots console to see Drones 1 and 2 detect the failure and re-calculate the search area in real-time.

---

## 📁 Project Structure
- `worlds/swarm_mission.wbt`: Forest environment with uneven terrain and 3 Mavic 2 Pro drones.
- `controllers/swarm_controller/`: Python logic for PID flight, heartbeats, and sectoring.
- `answers.md`: Full university assignment write-up including security analysis.

## 🛠️ Requirements
- **Webots R2025a** (or newer)
- **Python 3.10+** (standard Webots installation)
