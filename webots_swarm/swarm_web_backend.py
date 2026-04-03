import asyncio
import websockets
import json
import math
import time

GRID_SIZE = 100
FAILURE_TIME = 15

async def simulation_loop(websocket):
    print("Dashboard Connected!")
    
    time_elapsed = 0
    active_drones = [0, 1, 2]
    drone_pos = [[10.0, 10.0], [50.0, 10.0], [80.0, 10.0]]
    drone_z = [15.0, 15.0, 15.0]
    batteries = [100.0, 100.0, 100.0]
    
    curr_widths = [GRID_SIZE/3] * 3
    target_widths = [GRID_SIZE/3] * 3
    
    sectors = ["Sector A", "Sector B", "Sector C"]
    
    fire_active = False
    fire_pos = [65.0, 65.0]

    while True:
        try:
            # Poll for commands
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=0.01)
                data = json.loads(msg)
                if data.get("command") == "refresh":
                    time_elapsed = 0
                    active_drones = [0, 1, 2]
                    drone_pos = [[10.0, 10.0], [50.0, 10.0], [80.0, 10.0]]
                    batteries = [100.0, 100.0, 100.0]
                    curr_widths = [GRID_SIZE/3] * 3
                    target_widths = [GRID_SIZE/3] * 3
                    fire_active = False
                elif data.get("command") == "rtl":
                    batteries = [14.0, 14.0, 14.0]
                elif data.get("command") == "fire":
                    fire_active = True
                elif data.get("command") == "spoof":
                    gps_spoofed = True
            except (asyncio.TimeoutError, json.JSONDecodeError):
                pass

            time_elapsed += 0.1
            
            for i in list(active_drones):
                batteries[i] -= 0.05
                if batteries[i] < 15.0:
                    active_drones.remove(i)
                    rem = len(active_drones)
                    if rem > 0:
                        for j in range(3):
                            target_widths[j] = GRID_SIZE / rem if j in active_drones else 0
            
            if time_elapsed > FAILURE_TIME and 2 in active_drones:
                active_drones.remove(2)
                target_widths = [GRID_SIZE/2, GRID_SIZE/2, 0]
                
            for i in range(3):
                curr_widths[i] += (target_widths[i] - curr_widths[i]) * 0.1
                
            x_start = 0
            for i in range(3):
                if i in active_drones:
                    if fire_active and i == 0:
                        target_x = fire_pos[0]
                        target_y = fire_pos[1]
                        drone_pos[i][0] += (target_x - drone_pos[i][0]) * 0.05
                        drone_pos[i][1] += (target_y - drone_pos[i][1]) * 0.05
                        drone_z[i] = 45.0 + 2.0 * math.sin(time_elapsed * 5)
                        x_start += curr_widths[i]
                    else:
                        target_x = x_start + curr_widths[i]/2 + (curr_widths[i]/2.5) * math.sin(time_elapsed * 2 + i)
                        drone_pos[i][0] += (target_x - drone_pos[i][0]) * 0.1
                        drone_pos[i][1] = (drone_pos[i][1] + 0.8) % GRID_SIZE
                        drone_z[i] = 115.0 + 5.0 * math.sin(time_elapsed + i)
                        x_start += curr_widths[i]
                else:
                    drone_z[i] = max(0, drone_z[i] - 2.5)
                    x_start += curr_widths[i]
            
            payload = []
            for i in range(3):
                # Simulated GPS Spoofing Attack/Defense logic
                status_str = "ACTIVE" if i in active_drones else ("RTB" if batteries[i]<20 else "OFFLINE")
                sector_str = sectors[i] if i in active_drones else "N/A"
                
                # If spoofed, we pick Drone 2 (index 1) to "jitter" but the onboard fusion detects it
                display_x = drone_pos[i][0]
                display_y = drone_pos[i][1]
                
                if gps_spoofed and i == 1:
                    import random
                    # The "Spoof" jitter
                    display_x += random.uniform(-15.0, 15.0)
                    display_y += random.uniform(-15.0, 15.0)
                    status_str = "GPS ANOMALY"
                    sector_str = "STATION KEEPING"
                
                if fire_active and i == 0:
                    status_str = "RESPONDING"
                    sector_str = "FIRE INVESTIGATION"

                payload.append({
                    "id": f"d{i+1}",
                    "x": display_x,
                    "y": display_y,
                    "z": drone_z[i],
                    "battery": batteries[i],
                    "status": status_str,
                    "sector": sector_str,
                    "fire_active": fire_active,
                    "fire_pos_x": fire_pos[0],
                    "fire_pos_y": fire_pos[1]
                })
                
            await websocket.send(json.dumps(payload))
            await asyncio.sleep(0.1)
            
        except websockets.exceptions.ConnectionClosed:
            print("Dashboard Disconnected.")
            break

async def main():
    async with websockets.serve(simulation_loop, "localhost", 8765):
        print("Backend WebSocket Server running on ws://localhost:8765...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
