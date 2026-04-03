import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
import numpy as np

# --- Swarm Configuration ---
GRID_SIZE = 100
DRONES = ["Alpha (D1)", "Bravo (D2)", "Charlie (D3)"]
COLORS = ["#3498db", "#2ecc71", "#e74c3c"]
FAILURE_TIME = 15

class Building:
    def __init__(self, x, y, w, h, z, color, name):
        self.x, self.y, self.w, self.h, self.z = x, y, w, h, z
        self.color = color
        self.name = name

class SwarmSim3D:
    def __init__(self):
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(14, 8))
        
        # Grid Layout: 3D map on left, 3 POV cameras on right
        gs = GridSpec(3, 4, figure=self.fig, width_ratios=[1, 1, 1, 0.8])
        self.ax = self.fig.add_subplot(gs[:, :-1], projection='3d')
        
        # POV Camera Subplots
        self.cam_axes = []
        self.cam_images = []
        for i in range(3):
            ax = self.fig.add_subplot(gs[i, -1])
            ax.set_title(f"{DRONES[i]} Target Cam", color=COLORS[i], fontsize=10, pad=3)
            ax.set_xticks([])
            ax.set_yticks([])
            # Initialize with dummy data
            dummy_img = np.zeros((30, 30))
            img = ax.imshow(dummy_img, cmap='inferno', vmin=0, vmax=160)
            self.cam_axes.append(ax)
            self.cam_images.append(img)
            
        # Global 3D styling
        self.ax.set_xlim(0, GRID_SIZE)
        self.ax.set_ylim(0, GRID_SIZE)
        self.ax.set_zlim(0, 160)
        self.fig.suptitle("Digital Twin Site Monitoring & Drone POV", fontsize=16, y=0.96)
        
        self.ax.set_facecolor('#111111')
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False

        # Enhanced Construction Site Buildings
        self.buildings = [
            Building(10, 20, 20, 30, 45, '#7f8c8d', 'Concrete Base'),
            Building(40, 45, 25, 25, 80, '#e67e22', 'Steel Scaffold'),
            Building(70, 10, 20, 40, 110, '#95a5a6', 'Main Tower Core'),
            Building(20, 70, 15, 15, 25, '#c0392b', 'Brick Stack'),
            Building(80, 70, 15, 20, 15, '#2c3e50', 'Equip. Depot'),
            Building(5, 5, 25, 10, 10, '#34495e', 'Trailer Office')
        ]
        
        # Create an elevation heatmap for the drone cameras to "see"
        self.elevation_map = np.zeros((GRID_SIZE, GRID_SIZE))
        for b in self.buildings:
            self.elevation_map[b.y:b.y+b.h, b.x:b.x+b.w] = b.z
            
        # Draw Buildings as 3D Bars
        z3 = np.zeros(len(self.buildings))
        dx = [b.w for b in self.buildings]
        dy = [b.h for b in self.buildings]
        dz = [b.z for b in self.buildings]
        x_pos = [b.x for b in self.buildings]
        y_pos = [b.y for b in self.buildings]
        colors = [b.color for b in self.buildings]
        
        self.ax.bar3d(x_pos, y_pos, z3, dx, dy, dz, color=colors, alpha=0.5, edgecolor='black', linewidth=0.5, zsort='average')
        
        # Add labels
        for b in self.buildings:
            self.ax.text(b.x + b.w/2, b.y + b.h/2, b.z + 5, f"{b.name}\n({b.z}m)", 
                         color='white', fontsize=7, ha='center')

        self.cranes = []
        self.crane_artists = []
        self.drone_plots = []
        for c in COLORS:
            p, = self.ax.plot([], [], [], marker='X', color=c, markersize=14, markeredgecolor='white', linestyle='None')
            self.drone_plots.append(p)
            
        self.sector_lines = []
        for c in COLORS:
            l, = self.ax.plot([], [], [], color=c, alpha=0.3, linewidth=2)
            self.sector_lines.append(l)

        # HUD
        self.status_text = self.fig.text(0.01, 0.95, "", color='white', fontsize=10, verticalalignment='top')
        self.alert_text = self.fig.text(0.5, 0.5, "", color='red', fontsize=24, weight='bold', horizontalalignment='center', alpha=0)
        
        # State
        self.time = 0
        self.active_drones = [0, 1, 2]
        self.drone_pos = [[10, 10], [50, 10], [80, 10]]
        self.drone_z = [15.0, 15.0, 15.0]
        self.batteries = [100.0, 100.0, 100.0]
        self.patterns = ["Orthomosaic Grid", "Topographical Zig-Zag", "Circular Scan"]
        self.pattern_idx = 0
        self.area_scanned = 0.0
        
        self.curr_widths = [GRID_SIZE/3] * 3
        self.target_widths = [GRID_SIZE/3] * 3
        
        self.frame_offset = 0
        self.current_frame = 0
        
        from matplotlib.lines import Line2D
        custom_lines = [Line2D([0], [0], color=c, marker='X', markersize=10, linestyle='None') for c in COLORS]
        self.ax.legend(custom_lines, DRONES, loc='upper left', bbox_to_anchor=(0, 0.9), facecolor='black', edgecolor='white')
        
        # Listeners
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.text(0.01, 0.02, "Controls: [P] Flight Pattern | [C] Spawn Obstacle (Crane) | [R] Restart | [B] Drain D1 Battery", color='cyan', fontsize=11)
        
    def on_key_press(self, event):
        if event.key == 'r':
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
            
            self.cranes = []
            for ca in self.crane_artists:
                 try: ca.remove()
                 except: pass
            self.crane_artists = []
            
            # Reset POV cameras
            for i in range(3):
                self.cam_axes[i].set_title(f"{DRONES[i]} Target Cam", color=COLORS[i])
                
            # Reset Elevation map (remove crane)
            self.elevation_map = np.zeros((GRID_SIZE, GRID_SIZE))
            for b in self.buildings:
                self.elevation_map[b.y:b.y+b.h, b.x:b.x+b.w] = b.z
                
        elif event.key == 'b':
            if 0 in self.active_drones:
                self.batteries[0] = 14.9
                
        elif event.key == 'c':
            cx = self.drone_pos[0][0]
            cy = (self.drone_pos[0][1] + 15) % GRID_SIZE
            self.cranes.append(Building(cx-5, cy-5, 10, 10, 150, '#e74c3c', 'Crane'))
            
            # Update heatmap for POV
            c_ymin, c_ymax = int(max(0, cy-5)), int(min(GRID_SIZE, cy+5))
            c_xmin, c_xmax = int(max(0, cx-5)), int(min(GRID_SIZE, cx+5))
            self.elevation_map[c_ymin:c_ymax, c_xmin:c_xmax] = 150
            
            bar = self.ax.bar3d([cx-5], [cy-5], [0], [10], [10], [150], color='red', alpha=0.8, edgecolor='cyan')
            txt = self.ax.text(cx, cy, 160, "CRANE\n(150m)", color='white', fontsize=8, weight='bold')
            self.crane_artists.extend([bar, txt])
                
        elif event.key == 'p':
            self.pattern_idx = (self.pattern_idx + 1) % len(self.patterns)

    def get_ground_elevation(self, x, y):
        # We can just query our heatmap!
        iy, ix = int(y), int(x)
        if 0 <= iy < GRID_SIZE and 0 <= ix < GRID_SIZE:
            return self.elevation_map[iy, ix]
        return 0

    def get_pov_slice(self, x, y):
        FOV = 15  # View a 30x30 slice
        iy, ix = int(y), int(x)
        y_min, y_max = max(0, iy-FOV), min(GRID_SIZE, iy+FOV)
        x_min, x_max = max(0, ix-FOV), min(GRID_SIZE, ix+FOV)
        
        # Pad if edge of grid to keep 30x30 matrix steady
        slice_2d = self.elevation_map[y_min:y_max, x_min:x_max]
        
        # Quick padding trick to stabilize view
        padded = np.zeros((FOV*2, FOV*2))
        pad_y = FOV - (iy - y_min)
        pad_x = FOV - (ix - x_min)
        h, w = slice_2d.shape
        padded[pad_y:pad_y+h, pad_x:pad_x+w] = slice_2d
        
        # Include drone crosshair overlay marker in the center (highest value color)
        padded[FOV, FOV] = 160 
        return padded

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
                self.cam_axes[i].set_title(f"{DRONES[i]} GOING OFFLINE", color='gray')
                self.cam_images[i].set_data(np.zeros((30,30))) # Feed lost
        
        if self.time > FAILURE_TIME and 2 in self.active_drones:
            self.active_drones.remove(2)
            self.target_widths = [GRID_SIZE/2, GRID_SIZE/2, 0]
            self.alert_text.set_text("!!! HARDWARE MALFUNCTION DETECTED !!!")
            self.alert_text.set_alpha(1.0)
            self.cam_axes[2].set_title("FEED LOST", color='gray')
            self.cam_images[2].set_data(np.zeros((30,30)))
        
        if self.time > FAILURE_TIME + 3:
            curr_alpha = self.alert_text.get_alpha()
            if curr_alpha > 0: self.alert_text.set_alpha(max(0, curr_alpha - 0.05))

        for i in range(3):
            self.curr_widths[i] += (self.target_widths[i] - self.curr_widths[i]) * 0.1
        
        x_start = 0
        for i in range(3):
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
                
                # UPDATE POV CAMERA FEED
                self.cam_images[i].set_data(self.get_pov_slice(self.drone_pos[i][0], self.drone_pos[i][1]))
                
            else:
                self.drone_z[i] = max(0, self.drone_z[i] - 1.5)
            
            self.drone_plots[i].set_data([self.drone_pos[i][0]], [self.drone_pos[i][1]])
            self.drone_plots[i].set_3d_properties([self.drone_z[i]])
            x_start += self.curr_widths[i]

        if 2 not in self.active_drones:
            self.drone_plots[2].set_color('#555555')

        # Camera Pan
        self.ax.view_init(elev=40, azim=-60 + (self.time * 1.5))

        status = f"SURVEY TEAM {len(self.active_drones)}/3"
        batt_str = f"BATT: D1:{self.batteries[0]:.0f}% D2:{self.batteries[1]:.0f}% D3:{self.batteries[2]:.0f}%"
        self.status_text.set_text(f"TIME: {self.time:.1f}s | STATUS: {status} | PROGRESS: {self.area_scanned:.1f}%\nPATTERN: {self.patterns[self.pattern_idx]}\n{batt_str}")
        
        return self.drone_plots + self.sector_lines + self.cam_images

sim = SwarmSim3D()
ani = animation.FuncAnimation(sim.fig, sim.update, frames=600, interval=50, blit=False)
plt.tight_layout()
plt.show()
