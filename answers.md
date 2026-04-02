# Drone Swarm: Search and Rescue (SAR) Mission

**Group 3 - University Robotics Systems Assignment**

--------------------------------------------------

### 1. FINAL SWARM ALGORITHM

This algorithm uses a "Dynamic Sectoring" logic. Basically, we split the search area into slices and adjust based on who is still flying.

*   **Step 1: Initialization** – Drones sync their internal clocks and confirm the search boundary coordinates via a pre-flight handshake.
*   **Step 2: Sector Map** – The lead drone (Drone 1) divides the area into 3 equal strips. Drones 2 and 3 acknowledge their assigned sectors.
*   **Step 3: Parallel Sweep** – Drones move to the start of their strips. They fly a "lawnmower" pattern (back and forth) at a fixed altitude using visual sensors for detection.
*   **Step 4: Proximity Check** – Every 5 seconds, drones swap GPS coordinates. If a neighbor's coordinate hasn't updated, the swarm assumes a crash or stall.
*   **Step 5: Discovery & Convergence** – If a drone sees the target, it registers a "TARGET_FOUND" state. The active drones stop their lawnmower search and mathematically converge into a triangular hover formation directly above the target coordinates to provide multi-angle lighting, relay visual data, and ensure redundant coverage.
*   **Step 6: Task Re-allocation** – If a drone hits 15% battery or goes offline, it broadcasts "RETURNING_HOME" or is dropped from the heartbeat. The remaining drones re-calculate the remaining area and split it between themselves.

--------------------------------------------------

### 2. THE 4 CORE ASPECTS

*   **Priority: Coverage Speed**
    Drones fly at the max stable velocity (around 10m/s) to cover the area as fast as possible. We need to find the person before nightfall or battery runs out.
*   **Sacrifice: Data Redundancy**
    We don't send high-res video back to the base station constantly because it eats bandwidth. We only send low-res thumbnails or "Target Confirmed" flags.
*   **What can go wrong: Sensor False Positives**
    The simple rule-based vision might flag a logs or a bright rock as a human.
*   **Consequences: Time Wastage**
    The whole swarm might converge on a "nothing" target, wasting 10-15% of the total battery life before realizing the mistake and resetting the search.

--------------------------------------------------

### 3. COMMUNICATION & STRUCTURE

*   **Hybrid Structure:** It’s mostly decentralized for safety (drones avoid each other locally), but Drone 1 acts as a "soft leader" for initial tasking. If Drone 1 dies, Drone 2 is programmed to take over the math.
*   **Message Passing:** We use simple UDP string packets over a 2.4GHz mesh network. Messages look like: `ID:2|STAT:OK|POS:45.1,-75.2|BATT:80`.
*   **Comms Failure:** if a drone doesn't hear a "heartbeat" from the others for 30 seconds, it triggers a "Fail-Safe Scan." It continues its current sector but rises 20 meters to avoid hitting any other potential drones and then heads back to the launch point.

--------------------------------------------------

### 4. ATTACKS AND DEFENSES

**Attack 1: GPS Spoofing**
*   **Description:** An attacker broadcasts fake GPS signals with higher power than the satellites to make the drone think it's somewhere else.
*   **Defense:** We implement a "Consistency Check." The drone compares GPS movement against its internal IMU (Inertial Measurement Unit) and optical flow. If GPS says we moved 100m but the sensors say we stayed still, the drone ignores GPS and enters a hover.
*   **Survival:** The drone won't crash; it just stops moving blindly and waits for manual override.

**Attack 2: Command Replay Attack**
*   **Description:** An attacker captures a "TARGET_FOUND" packet and replays it later from a different location.
*   **Defense:** Every message includes a "Sequence Number" and a "Timestamp." If the drone receives a message with an old timestamp or a sequence number it already saw, it just drops it.
*   **Survival:** The swarm ignores the fake "found" signal and keeps searching the actual area.

**Attack 3: De-authentication (WiFi Jamming)**
*   **Description:** Attacker floods the 2.4GHz band with noise so drones can't talk.
*   **Defense:** "Last Known Assignment" persistence. If the mesh goes down, the drones don't just stop. They finish their current assigned sector autonomously before returning home.
*   **Survival:** The mission takes longer and coordination is gone, but 60-70% of the area still gets searched.

--------------------------------------------------

### 5. SIMPLE DEMONSTRATION EXAMPLE (SIMULATION RESULTS)

We built an interactive Python 2D simulation of the 3-drone swarm on a 500m x 500m grid. 

**Demonstration Controls:**
*   **[H] Hide Target:** Toggles the target on/off. Hiding the target allows the swarm to demonstrate 100% map coverage and continuous scanning instead of stopping at T+25s.
*   **[R] Restart:** Instantly resets the simulation back to T=0s.

**Scenario History:**
1.  **Start:** Drones Alpha (D1), Bravo (D2), and Charlie (D3) start searching their assigned sectors.
2.  **Attack:** At T+15s, Charlie (D3) experiences a **Jamming Attack** and stops sending heartbeats.
3.  **Reaction:** At T+16s, Alpha and Bravo recognize the loss of contact and **automatically re-allocate** Charlie's sector between them.
4.  **Success:** At T+25s, Alpha detects the target.

**Detailed Simulation Log Snapshot:**
```text
T+15s:
  Heartbeat: [1, 2, 3] active
  [!] ALERT: Drone 3 Comm interference detected (JAMMING ATTACK)
  D1: POS(0, 60) | BATT:99.4%
  D2: POS(0, 60) | BATT:99.4%

T+16s:
  Heartbeat: [1, 2] active
  [SYSTEM] Drone 3 lost. Re-allocating sector 334-500 to Drones 1 & 2...
  D1: POS(0, 70) | BATT:99.3%
  D2: POS(0, 70) | BATT:99.3%

...

T+25s:
  Heartbeat: [1, 2] active
  [FOUND] Drone 1 spotted target!

--- MISSION SUCCESS ---
```

--------------------------------------------------
*Scaling this could involve light ML for better recognition, but the rule-based logic ensures reliability even when the network is under attack.*
