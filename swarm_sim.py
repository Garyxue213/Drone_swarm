import time
import random

class Drone:
    def __init__(self, drone_id, sector_range):
        self.drone_id = drone_id
        self.x, self.y = 0, 0
        self.battery = 100.0
        self.status = "OK" # OK, JAMMED, BUSY
        self.sector_range = sector_range # (min_x, max_x)
        self.path_y_direction = 1 # 1: up, -1: down
        self.is_returning = False
        self.target_found = None

    def move(self):
        if self.status == "JAMMED" or self.battery <= 0:
            return

        # Simple lawnmower pattern
        # Stay within x sector, move y up and down
        if not self.is_returning:
            self.y += 10 * self.path_y_direction
            if self.y >= 500 or self.y <= 0:
                self.path_y_direction *= -1
                self.x += 20 # Step over
                if self.x > self.sector_range[1]:
                    self.x = self.sector_range[0] # Restart sector if needed (looping for sim)

            self.battery -= 0.1
        else:
            # Fly to (0,0)
            self.x = max(0, self.x - 10)
            self.y = max(0, self.y - 10)
            if self.x == 0 and self.y == 0:
                self.status = "LANDED"

    def check_target(self, target_pos):
        if self.status != "OK": return False
        # If within 15 meters
        dist = ((self.x - target_pos[0])**2 + (self.y - target_pos[1])**2)**0.5
        if dist < 15:
            self.target_found = target_pos
            return True
        return False

def simulate_swarm():
    print("--- INITIATING SAR SWARM MISSION ---")
    print("Area: 500m x 500m | Drones: 3 | Mode: Dynamic Sectoring")
    
    target_pos = (0, 150) # Located on Drone 1's first sweep path
    drones = [
        Drone(1, (0, 166)),
        Drone(2, (167, 333)),
        Drone(3, (334, 500))
    ]
    
    mission_clock = 0
    mission_active = True
    
    while mission_active and mission_clock < 20: # 20 steps for demo
        print(f"\nT+{mission_clock}s:")
        
        # Communication / Heartbeat Check
        living_drones = [d for d in drones if d.status == "OK"]
        print(f"  Heartbeat: {[d.drone_id for d in living_drones]} active")
        
        # Attack Scenario: Jamming D3 at 5s
        if mission_clock == 5:
            print("  [!] ALERT: Drone 3 Comm interference detected (JAMMING ATTACK)")
            drones[2].status = "JAMMED"
            
        # Re-balancing Logic (if a drone is lost)
        if mission_clock == 6: # Reactive re-balancing
            print("  [SYSTEM] Drone 3 lost. Re-allocating sector 334-500 to Drones 1 & 2...")
            drones[0].sector_range = (0, 250)
            drones[1].sector_range = (251, 500)
            
        # Move and Search
        for d in drones:
            d.move()
            if d.check_target(target_pos):
                print(f"  [FOUND] Drone {d.drone_id} spotted target at {target_pos}!")
                mission_active = False
                break
            
            if d.status == "OK":
                print(f"  D{d.drone_id}: POS({d.x}, {d.y}) | BATT:{d.battery:.1f}%")
        
        mission_clock += 1
        # time.sleep(0.1) # Fast simulation

    if not mission_active:
        print("\n--- MISSION SUCCESS ---")
        print(f"Search concluded in {mission_clock} seconds.")
    else:
        print("\n--- MISSION TIMEOUT ---")

if __name__ == "__main__":
    simulate_swarm()
