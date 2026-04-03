import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
# Requires active Tkinter or Qt5 backend on standard systems, built-in Mac works best

# --- Swarm Configuration ---
GRID_SIZE = 100
DRONES = ["Alpha (D1)", "Bravo (D2)", "Charlie (D3)"]
COLORS = ["#3498db", "#2ecc71", "#e74c3c"]
FAILURE_TIME = 15

class Building:
    def __init__(self, x, y, w, h, z):
        self.x, self.y, self.w, self.h, self.z = x, y, w, h, z

class SwarmSim3D:
    def __init__(self):
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.ax.set_xlim(0, GRID_SIZE)
        self.ax.set_ylim(0, GRID_SIZE)
        self.ax.set_zlim(0, 160)
        self.ax.set_title("Construction Site 3D Mapping & Safety Simulation", fontsize=14, pad=20)
        
        # Grid Styling
        self.ax.set_facecolor('#1e1e1e')
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False

        # Buildings (Simulating an incomplete structure)
        self.buildings = [
            Building(10, 20, 20, 30, 45),
            Building(40, 50, 25, 20, 80),
            Building(70, 10, 20, 40, 110)
        ]
        
        # Draw Buildings as 3D Bars
        z3 = np.zeros(len(self.buildings))
        dx = [b.w for b in self.buildings]
        dy = [b.h for b in self.buildings]
        dz = [b.z for b in self.buildings]
        x_pos = [b.x for b in self.buildings]
        y_pos = [b.y for b in self.buildings]
        
        self.ax.bar3d(x_pos, y_pos, z3, dx, dy, dz, color='#f1c40f', alpha=0.4, edgecolor='#f39c12', zsort='average')
        
        # Add labels floating above buildings
        for b in self.buildings:
            self.ax.text(b.x, b.y, b.z + 5, f"Elev: {b.z}m", color='white', fontsize=8)

        self.cranes = []
        self.crane_artists = []
        
        # Drone Models
        self.drone_plots = []
        for c in COLORS:
            p, = self.ax.plot([], [], [], marker='X', color=c, markersize=12, markeredgecolor='white', linestyle='None')
            self.drone_plots.append(p)
            
        # Sector bounding paths overlayed on ground
        self.sector_lines = []
        for c in COLORS:
            l, = self.ax.plot([], [], [], color=c, alpha=0.3, linewidth=2)
            self.sector_lines.append(l)

        # HUD / Texts overlay
        self.status_text = self.fig.text(0.02, 0.95, "", color='white', fontsize=10, verticalalignment='top')
        self.elev_text = self.fig.text(0.85, 0.95, "", color='white', fontsize=10, verticalalignment='top')
        self.alert_text = self.fig.text(0.5, 0.5, "", color='red', fontsize=20, weight='bold', horizontalalignment='center', alpha=0)
        
        # Swarm Logic State
        self.time = 0
        self.active_drones = [0, 1, 2]
        self.drone_pos = [[10, 10], [50, 10], [80, 10]]
        self.drone_z = [15.0, 15.0, 15.0]
        self.batteries = [100.0, 100.0, 100.0]
        self.patterns = ["Orthomosaic Grid", "Topographical Zig-Zag", "Circular Scan"]
        self.pattern_idx = 0
        self.area_scanned = 0.0
        
        # Smooth Sector Logic
        self.curr_widths = [GRID_SIZE/3] * 3
        self.target_widths = [GRID_SIZE/3] * 3
        
        self.frame_offset = 0
        self.current_frame = 0
        
        # Legend (Using proxy artists for clean UI)
        from matplotlib.lines import Line2D
        custom_lines = [Line2D([0], [0], color=c, marker='X', markersize=10, linestyle='None') for c in COLORS]
        self.ax.legend(custom_lines, DRONES, loc='upper right', facecolor='black', edgecolor='white')
        
        # Listeners
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.text(0.02, 0.02, "Controls: [P] Flight Pattern | [C] Spawn Obstacle (Crane) | [R] Restart | [B] Drain D1 Battery", color='gray', fontsize=10)
        
    def on_key_press(self, event):
        if event.key == 'r':
            print("[SYSTEM] Restarting Simulation")
            self.frame_offset += self.current_frame
            self.time = 0
            self.active_drones = [0, 1, 2]
            self.drone_pos = [[10, 10], [50, 10], [80, 10]]
            self.drone_z = [15.0, 15.0, 15.0]
            self.curr_widths = [GRID_SIZE/3] * 3
            self.target_widths = [GRID_SIZE/3] * 3
            self.alert_text.set_alpha(0)
            self.batteries = [100.0, 100.0, 100.0]
            self.area_scanned = 0.0
            
            # Clear Objects
            self.cranes = []
            for ca in self.crane_artists:
                 try: ca.remove()
                 except: pass
            self.crane_artists = []
            
            for i, dp in enumerate(self.drone_plots):
                dp.set_color(COLORS[i])
                dp.set_alpha(1.0)
                
        elif event.key == 'b':
            if 0 in self.active_drones:
                self.batteries[0] = 14.9
                print("[SYSTEM] Battery Drain Triggered! Alpha (D1) at critical battery.")
                
        elif event.key == 'c':
            cx = self.drone_pos[0][0]
            cy = (self.drone_pos[0][1] + 15) % GRID_SIZE
            self.cranes.append(Building(cx-5, cy-5, 10, 10, 150))
            
            bar = self.ax.bar3d([cx-5], [cy-5], [0], [10], [10], [150], color='red', alpha=0.6, edgecolor='white')
            txt = self.ax.text(cx, cy, 160, "CRANE\n150m", color='white', fontsize=7, weight='bold')
            self.crane_artists.extend([bar, txt])
            print(f"[SYSTEM] High-Elevation Crane Obstacle spawned at ({cx:.0f}, {cy:.0f})!")
                
        elif event.key == 'p':
            self.pattern_idx = (self.pattern_idx + 1) % len(self.patterns)
            print(f"[SYSTEM] Switched Survey Pattern to: {self.patterns[self.pattern_idx]}")

    def get_ground_elevation(self, x, y):
        z = 0
        for b in self.buildings + self.cranes:
            if b.x <= x <= b.x + b.w and b.y <= y <= b.y + b.h:
                z = max(z, b.z)
        return z

    def update(self, frame):
        self.current_frame = frame - self.frame_offset
        self.time = self.current_frame / 10.0
        
        self.area_scanned = min(100.0, self.area_scanned + len(self.active_drones) * 0.03)
        
        for i in list(self.active_drones):
            self.batteries[i] -= 0.05
            if self.batteries[i] < 15.0:
                self.active_drones.remove(i)
                rem = len(self.active_drones)
                if rem > 0:
                    for j in range(3):
                        self.target_widths[j] = GRID_SIZE / rem if j in self.active_drones else 0
                self.alert_text.set_text(f"!!! {DRONES[i]} BATTERY LOW - RTB !!!")
                self.alert_text.set_alpha(1.0)
                self.drone_plots[i].set_color('#333333')
                self.drone_plots[i].set_alpha(0.5)
        
        if self.time > FAILURE_TIME and 2 in self.active_drones:
            self.active_drones.remove(2)
            self.target_widths = [GRID_SIZE/2, GRID_SIZE/2, 0]
            self.alert_text.set_text("!!! HARDWARE MALFUNCTION DETECTED !!!")
            self.alert_text.set_alpha(1.0)
        
        if self.time > FAILURE_TIME + 3:
            curr_alpha = self.alert_text.get_alpha()
            if curr_alpha > 0: self.alert_text.set_alpha(max(0, curr_alpha - 0.05))

        for i in range(3):
            self.curr_widths[i] += (self.target_widths[i] - self.curr_widths[i]) * 0.1
        
        x_start = 0
        for i in range(3):
            # Move Grid Lines identifying sectors on floor (Z=1)
            self.sector_lines[i].set_data([x_start, x_start, x_start+self.curr_widths[i], x_start+self.curr_widths[i], x_start],
                                          [0, GRID_SIZE, GRID_SIZE, 0, 0])
            self.sector_lines[i].set_3d_properties([1, 1, 1, 1, 1])

            if i in self.active_drones:
                pattern = self.patterns[self.pattern_idx]
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

                ground_z = self.get_ground_elevation(self.drone_pos[i][0], self.drone_pos[i][1])
                target_z = ground_z + 15
                self.drone_z[i] += (target_z - self.drone_z[i]) * 0.2
            else:
                self.drone_z[i] = max(0, self.drone_z[i] - 1.5)  # Quick drop to ground if disabled
            
            # Map Drone 3D Location
            self.drone_plots[i].set_data([self.drone_pos[i][0]], [self.drone_pos[i][1]])
            self.drone_plots[i].set_3d_properties([self.drone_z[i]])
            x_start += self.curr_widths[i]

        if 2 not in self.active_drones:
            self.drone_plots[2].set_color('#555555')

        # Camera Pan - Panning the 3D map automatically makes analyzing topography look gorgeous
        self.ax.view_init(elev=35, azim=-60 + (self.time * 1.5))

        # HUD Update
        status = f"SURVEY TEAM {len(self.active_drones)}/3"
        batt_str = f"BATT: D1:{self.batteries[0]:.0f}% D2:{self.batteries[1]:.0f}% D3:{self.batteries[2]:.0f}%"
        self.status_text.set_text(f"TIME: {self.time:.1f}s\nSTATUS: {status}\nPROGRESS: {self.area_scanned:.1f}%\nPATTERN: {self.patterns[self.pattern_idx]}\n{batt_str}")
        
        elev_str = "ELEVATION (Z-AXIS):\n" + "\n".join([f"{DRONES[i]}: {self.drone_z[i]:.1f}m" for i in range(3) if i in self.active_drones])
        self.elev_text.set_text(elev_str)

        return self.drone_plots + self.sector_lines # Don't return Text for 3d blit reasons

sim = SwarmSim3D()
ani = animation.FuncAnimation(sim.fig, sim.update, frames=600, interval=50, blit=False)
plt.show()
