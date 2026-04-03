import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
import numpy as np

# --- Swarm Configuration ---
GRID_SIZE = 100
DRONES = ["Alpha (D1)", "Bravo (D2)", "Charlie (D3)"]
COLORS = ["#3498db", "#2ecc71", "#e74c3c"] # Modern Blue, Green, Red
FAILURE_TIME = 15  # Seconds until D3 Equipment malfunction 

class Building:
    def __init__(self, x, y, w, h, z):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.z = z  # Elevation height

class SwarmSim2D:
    def __init__(self):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.set_xlim(0, GRID_SIZE)
        self.ax.set_ylim(0, GRID_SIZE)
        self.ax.set_title("Construction Site 3D Mapping & Safety Simulation", fontsize=14, pad=20)
        
        # Grid Styling
        self.ax.grid(color='white', alpha=0.1)
        self.ax.set_facecolor('#1e1e1e')

        # Topographical Buildings (x, y, w, h, z-elevation)
        self.buildings = [
            Building(10, 20, 20, 30, 45),
            Building(40, 50, 25, 20, 80),
            Building(70, 10, 20, 40, 110)
        ]
        
        # Draw Buildings
        for b in self.buildings:
            rect = patches.Rectangle((b.x, b.y), b.w, b.h, alpha=0.3, color='#f1c40f', ec='#f39c12', lw=2)
            self.ax.add_patch(rect)
            self.ax.text(b.x+2, b.y+2, f"Elev: {b.z}m", color='white', fontsize=8)
            
        self.cranes = []
        self.crane_plots = []
        
        # Sector Rectangles
        self.sector_rects = [plt.Rectangle((0, 0), 0, 0, alpha=0.10, color=c) for c in COLORS]
        for r in self.sector_rects: self.ax.add_patch(r)
        
        # Drone Models
        self.drone_plots = [self.ax.plot([], [], 'o', color=c, markersize=12, label=n, 
                            markeredgecolor='white', markeredgewidth=1)[0] 
                            for n, c in zip(DRONES, COLORS)]
        
        # HUD Text
        self.status_text = self.ax.text(2, 95, "", color='white', fontsize=10, verticalalignment='top')
        self.elev_text = self.ax.text(GRID_SIZE-25, 95, "", color='white', fontsize=10, verticalalignment='top')
        self.alert_text = self.ax.text(50, 50, "", color='red', fontsize=20, 
                                       weight='bold', horizontalalignment='center', alpha=0)
        
        # State
        self.time = 0
        self.active_drones = [0, 1, 2]
        self.drone_pos = [[10, 10], [50, 10], [80, 10]]
        self.drone_z = [15.0, 15.0, 15.0]
        self.batteries = [100.0, 100.0, 100.0]
        self.patterns = ["Orthomosaic Grid", "Topographical Zig-Zag", "Circular Scan"]
        self.pattern_idx = 0
        self.area_scanned = 0.0
        
        # Smooth Sector Resize State
        self.curr_widths = [GRID_SIZE/3] * 3
        self.target_widths = [GRID_SIZE/3] * 3
        
        self.frame_offset = 0
        self.current_frame = 0
        
        self.ax.legend(loc='lower right', frameon=True, facecolor='black')
        
        # Keyboard Listener
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.ax.text(2, 2, "Controls: [P] Flight Pattern | [C] Spawn Obstacle (Crane) | [R] Restart | [B] Drain D1", color='gray', fontsize=10)
        
    def on_key_press(self, event):
        if event.key == 'r':
            print("[SYSTEM] Restarting Simulation")
            self.frame_offset += self.current_frame
            self.time = 0
            self.active_drones = [0, 1, 2]
            self.drone_pos = [[10, 10], [50, 10], [80, 10]]
            self.curr_widths = [GRID_SIZE/3] * 3
            self.target_widths = [GRID_SIZE/3] * 3
            self.alert_text.set_alpha(0)
            self.batteries = [100.0, 100.0, 100.0]
            self.area_scanned = 0.0
            
            # Clear Cranes
            self.cranes = []
            for cp in self.crane_plots:
                try: cp.remove()
                except: pass
            self.crane_plots = []
            
            for i, dp in enumerate(self.drone_plots):
                dp.set_color(COLORS[i])
                dp.set_alpha(1.0)
                
        elif event.key == 'b':
            if 0 in self.active_drones:
                self.batteries[0] = 14.9
                print("[SYSTEM] Battery Drain Triggered! Alpha (D1) at critical battery.")
                
        elif event.key == 'c':
            # Spawn a Crane obstacle at D1's path
            cx = self.drone_pos[0][0]
            cy = (self.drone_pos[0][1] + 15) % GRID_SIZE
            self.cranes.append(Building(cx-5, cy-5, 10, 10, 150)) # Crane 150m tall
            
            # Plot it
            cp = patches.Rectangle((cx-5, cy-5), 10, 10, alpha=0.9, color='red', ec='white', lw=1)
            self.crane_plots.append(cp)
            self.ax.add_patch(cp)
            
            # Text label
            txt = self.ax.text(cx-4, cy-4, "CRANE\n150m", color='white', fontsize=7, weight='bold')
            self.crane_plots.append(txt) # Manage so it clears on Restart
            
            print(f"[SYSTEM] High-Elevation Crane Obstacle spawned at ({cx:.0f}, {cy:.0f})!")
                
        elif event.key == 'p':
            self.pattern_idx = (self.pattern_idx + 1) % len(self.patterns)
            print(f"[SYSTEM] Switched Survey Pattern to: {self.patterns[self.pattern_idx]}")

    def get_ground_elevation(self, x, y):
        # Determine highest obstacle at current x,y
        z = 0
        for b in self.buildings + self.cranes:
            if b.x <= x <= b.x + b.w and b.y <= y <= b.y + b.h:
                z = max(z, b.z)
        return z

    def update(self, frame):
        self.current_frame = frame - self.frame_offset
        self.time = self.current_frame / 10.0  # 10 FPS
        
        # Area Scanned (Progresses as long as drones are actively surveying)
        self.area_scanned = min(100.0, self.area_scanned + len(self.active_drones) * 0.03)
        
        # Battery Logic (Step 6)
        for i in list(self.active_drones):
            self.batteries[i] -= 0.05
            if self.batteries[i] < 15.0:
                print(f"[SYSTEM] {DRONES[i]} hit 15% Battery. Returning to Charge Station.")
                self.active_drones.remove(i)
                rem = len(self.active_drones)
                if rem > 0:
                    for j in range(3):
                        self.target_widths[j] = GRID_SIZE / rem if j in self.active_drones else 0
                self.alert_text.set_text(f"!!! {DRONES[i]} BATTERY LOW - RTB !!!")
                self.alert_text.set_alpha(1.0)
                self.drone_plots[i].set_color('#333333')
                self.drone_plots[i].set_alpha(0.5)
        
        # Hardware Malfunction Attack/Loss
        if self.time > FAILURE_TIME and 2 in self.active_drones:
            self.active_drones.remove(2)
            self.target_widths = [GRID_SIZE/2, GRID_SIZE/2, 0] # Re-allocate remaining width
            self.alert_text.set_text("!!! HARDWARE MALFUNCTION DETECTED !!!")
            self.alert_text.set_alpha(1.0)
        
        if self.time > FAILURE_TIME + 3:
            curr_alpha = self.alert_text.get_alpha()
            if curr_alpha > 0: self.alert_text.set_alpha(max(0, curr_alpha - 0.05))

        # Smooth Sector Resize logic
        for i in range(3):
            self.curr_widths[i] += (self.target_widths[i] - self.curr_widths[i]) * 0.1
        
        # Update Visuals
        x_start = 0
        for i in range(3):
            self.sector_rects[i].set_xy((x_start, 0))
            self.sector_rects[i].set_width(self.curr_widths[i])
            self.sector_rects[i].set_height(GRID_SIZE)
            
            if i in self.active_drones:
                pattern = self.patterns[self.pattern_idx]
                
                # Survey Search Patterns
                if pattern == "Orthomosaic Grid":
                    target_x = x_start + self.curr_widths[i]/2
                    self.drone_pos[i][0] += (target_x - self.drone_pos[i][0]) * 0.1
                    self.drone_pos[i][1] = (self.drone_pos[i][1] + 1) % GRID_SIZE
                elif pattern == "Topographical Zig-Zag":
                    target_x = x_start + self.curr_widths[i]/2 + (self.curr_widths[i]/2.5) * np.sin(self.time * 2 + i)
                    self.drone_pos[i][0] += (target_x - self.drone_pos[i][0]) * 0.1
                    self.drone_pos[i][1] = (self.drone_pos[i][1] + 0.8) % GRID_SIZE
                elif pattern == "Circular Scan":
                    target_x = x_start + self.curr_widths[i]/2 + (self.curr_widths[i]/2.5) * np.cos(self.time * 2 + i)
                    target_y = 50 + 40 * np.sin(self.time * 2 + i)
                    self.drone_pos[i][0] += (target_x - self.drone_pos[i][0]) * 0.1
                    self.drone_pos[i][1] += (target_y - self.drone_pos[i][1]) * 0.1

                # Dynamic Altimeter Calculations (Dodging Buildings / Cranes)
                # Drones maintain a safe altitude of 15m above the highest topographical feature
                ground_z = self.get_ground_elevation(self.drone_pos[i][0], self.drone_pos[i][1])
                target_z = ground_z + 15
                self.drone_z[i] += (target_z - self.drone_z[i]) * 0.2
            
            # Map size adjustments for plotting based on Z-height to fake a 3D perspective effect
            size = max(6, min(25, self.drone_z[i] / 5)) if i in self.active_drones else 12
            self.drone_plots[i].set_markersize(size)
            self.drone_plots[i].set_data([self.drone_pos[i][0]], [self.drone_pos[i][1]])
            x_start += self.curr_widths[i]

        if 2 not in self.active_drones:
            self.drone_plots[2].set_color('#555555')
            self.drone_plots[2].set_alpha(0.5)

        # Update HUD Text
        status = f"SURVEY TEAM {len(self.active_drones)}/3"
        batt_str = f"BATT: D1:{self.batteries[0]:.0f}% D2:{self.batteries[1]:.0f}% D3:{self.batteries[2]:.0f}%"
        self.status_text.set_text(f"TIME: {self.time:.1f}s\nSTATUS: {status}\nPROGRESS: {self.area_scanned:.1f}%\nPATTERN: {self.patterns[self.pattern_idx]}\n{batt_str}")
        
        elev_str = "ELEVATION (Z-AXIS):\n" + "\n".join([f"{DRONES[i]}: {self.drone_z[i]:.1f}m" for i in range(3) if i in self.active_drones])
        self.elev_text.set_text(elev_str)

        return self.drone_plots + self.sector_rects + [self.status_text, self.elev_text, self.alert_text]

sim = SwarmSim2D()
ani = animation.FuncAnimation(sim.fig, sim.update, frames=600, interval=50, blit=True)
plt.tight_layout()
plt.show()
