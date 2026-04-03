import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LightSource
import numpy as np

# --- Swarm Configuration ---
GRID_SIZE = 100
DRONES = ["Alpha (D1)", "Bravo (D2)", "Charlie (D3)"]
COLORS = ["#0000FF", "#00FF00", "#FF0000"] # High contrast Primary colors
FAILURE_TIME = 15

class Building:
    def __init__(self, x, y, w, h, z, color, name):
        self.x, self.y, self.w, self.h, self.z = x, y, w, h, z
        self.color = color
        self.name = name
        self.ground_z = 0  # To be calculated based on terrain

class SwarmSim3D:
    def __init__(self):
        # Swap from dark theme to realistic daylight theme
        plt.style.use('default')
        self.fig = plt.figure(figsize=(14, 8))
        self.fig.patch.set_facecolor('#dceeff')  # Sky blue background
        
        # Grid Layout
        gs = GridSpec(3, 4, figure=self.fig, width_ratios=[1, 1, 1, 0.8])
        self.ax = self.fig.add_subplot(gs[:, :-1], projection='3d')
        self.ax.set_facecolor('#dceeff')
        
        # POV Camera Subplots
        self.cam_axes = []
        self.cam_images = []
        for i in range(3):
            ax = self.fig.add_subplot(gs[i, -1])
            ax.set_title(f"{DRONES[i]} Topological Cam", color='black', fontsize=10, pad=3)
            ax.set_xticks([])
            ax.set_yticks([])
            dummy_img = np.zeros((30, 30))
            img = ax.imshow(dummy_img, cmap='terrain', vmin=0, vmax=160)
            self.cam_axes.append(ax)
            self.cam_images.append(img)
            
        # Global 3D styling
        self.ax.set_xlim(0, GRID_SIZE)
        self.ax.set_ylim(0, GRID_SIZE)
        self.ax.set_zlim(0, 160)
        self.fig.suptitle("Digital Twin Site Monitoring & Drone POV", fontsize=16, y=0.96)

        # ---------------- REALISTIC TERRAIN GENERATION (Excavation Site) ----------------
        x_grid = np.linspace(0, GRID_SIZE, GRID_SIZE)
        y_grid = np.linspace(0, GRID_SIZE, GRID_SIZE)
        X, Y = np.meshgrid(x_grid, y_grid)
        
        # Mathematical procedural terrain (Hills and valleys)
        self.elevation_map = 8 * np.sin(X/12) * np.cos(Y/12) + 6 * np.sin(X/6) + 12
        self.elevation_map = np.clip(self.elevation_map, 2, None)
        
        # Shade the surface terrain based on a light source
        ls = LightSource(270, 45)
        rgb = ls.shade(self.elevation_map, cmap=plt.cm.terrain, vert_exag=1, blend_mode='soft')
        self.ax.plot_surface(X, Y, self.elevation_map, facecolors=rgb, rstride=1, cstride=1, linewidth=0, antialiased=True, alpha=0.9)

        # Buildings
        self.buildings = [
            Building(10, 20, 20, 30, 45, '#7f8c8d', 'Concrete Base'),
            Building(40, 45, 25, 25, 80, '#e67e22', 'Steel Scaffold'),
            Building(70, 10, 20, 40, 110, '#95a5a6', 'Main Tower Core'),
            Building(20, 70, 15, 15, 25, '#c0392b', 'Brick Stack'),
            Building(80, 70, 15, 20, 15, '#2c3e50', 'Equip. Depot'),
            Building(5, 5, 25, 10, 10, '#ffffff', 'Trailer Office')
        ]
        
        # Combine Buildings into Elevation Map and plot them realistically
        z3 = []
        dx, dy, dz, x_pos, y_pos, colors = [], [], [], [], [], []
        
        for b in self.buildings:
            # Find terrain height under building
            base_z = np.max(self.elevation_map[int(b.y):int(b.y+b.h), int(b.x):int(b.x+b.w)])
            b.ground_z = base_z
            # Imprint on map
            self.elevation_map[int(b.y):int(b.y+b.h), int(b.x):int(b.x+b.w)] = b.z + base_z
            
            x_pos.append(b.x)
            y_pos.append(b.y)
            z3.append(base_z) # Starts AT the terrain height
            dx.append(b.w)
            dy.append(b.h)
            dz.append(b.z)    # Rises by building height
            colors.append(b.color)

        # Solid Shaded 3D Bars for Realism
        self.ax.bar3d(x_pos, y_pos, z3, dx, dy, dz, color=colors, shade=True, alpha=1.0, zorder=10)
        
        for b in self.buildings:
            # Drop an indicator line / label above building
            self.ax.text(b.x + b.w/2, b.y + b.h/2, b.z + b.ground_z + 10, f"{b.name}", color='black', fontsize=8, ha='center', weight='bold')

        self.cranes = []
        self.crane_artists = []
        
        # ---------------- DRONE MODELS (Drop Shadows added for realism) ----------------
        self.drone_plots = []
        self.drone_shadows = [] # Thin lines connecting drone to ground for vertical perception
        for c in COLORS:
            p, = self.ax.plot([], [], [], marker='P', color=c, markersize=12, markeredgecolor='black', linestyle='None', zorder=20)
            s, = self.ax.plot([], [], [], color='black', linestyle='--', linewidth=0.8, alpha=0.5)
            self.drone_plots.append(p)
            self.drone_shadows.append(s)

        # HUD
        self.status_text = self.fig.text(0.01, 0.95, "", color='black', fontsize=11, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))
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
        
        # Listeners
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.text(0.01, 0.02, "Controls: [P] Flight Pattern | [C] Spawn Obstacle (Crane) | [R] Restart | [B] Drain D1 Battery", color='black', fontsize=11, weight='bold')
        
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
            
            for i in range(3):
                self.cam_axes[i].set_title(f"{DRONES[i]} Target Cam", color='black')
                
        elif event.key == 'b':
            if 0 in self.active_drones:
                self.batteries[0] = 14.9
                
        elif event.key == 'c':
            cx = self.drone_pos[0][0]
            cy = (self.drone_pos[0][1] + 15) % GRID_SIZE
            c_base_z = self.get_ground_elevation(cx, cy)
            self.cranes.append(Building(cx-5, cy-5, 10, 10, 150, '#e74c3c', 'Crane'))
            
            # Imprint Crane to Elevation Map
            c_ymin, c_ymax = int(max(0, cy-5)), int(min(GRID_SIZE, cy+5))
            c_xmin, c_xmax = int(max(0, cx-5)), int(min(GRID_SIZE, cx+5))
            self.elevation_map[c_ymin:c_ymax, c_xmin:c_xmax] = 150 + c_base_z
            
            bar = self.ax.bar3d([cx-5], [cy-5], [c_base_z], [10], [10], [150], color='#e74c3c', shade=True, alpha=1.0)
            txt = self.ax.text(cx, cy, c_base_z + 160, "CRANE\n(150m)", color='black', fontsize=9, weight='bold')
            self.crane_artists.extend([bar, txt])
                
        elif event.key == 'p':
            self.pattern_idx = (self.pattern_idx + 1) % len(self.patterns)

    def get_ground_elevation(self, x, y):
        iy, ix = int(y), int(x)
        if 0 <= iy < GRID_SIZE and 0 <= ix < GRID_SIZE:
            return self.elevation_map[iy, ix]
        return 0

    def get_pov_slice(self, x, y):
        FOV = 15
        iy, ix = int(y), int(x)
        y_min, y_max = max(0, iy-FOV), min(GRID_SIZE, iy+FOV)
        x_min, x_max = max(0, ix-FOV), min(GRID_SIZE, ix+FOV)
        
        slice_2d = self.elevation_map[y_min:y_max, x_min:x_max]
        
        padded = np.zeros((FOV*2, FOV*2))
        pad_y = FOV - (iy - y_min)
        pad_x = FOV - (ix - x_min)
        h, w = slice_2d.shape
        padded[pad_y:pad_y+h, pad_x:pad_x+w] = slice_2d
        
        padded[FOV, FOV] = 160 # Crosshair point
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
                self.drone_plots[i].set_color('#888888')
                self.cam_axes[i].set_title(f"{DRONES[i]} OFFLINE", color='gray')
                self.cam_images[i].set_data(np.zeros((30,30)))
        
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
            ground_z_now = self.get_ground_elevation(self.drone_pos[i][0], self.drone_pos[i][1])

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

                target_z = ground_z_now + 25  # Maintain 25m clearance natively
                self.drone_z[i] += (target_z - self.drone_z[i]) * 0.2
                
                # Update POV Cam feed
                self.cam_images[i].set_data(self.get_pov_slice(self.drone_pos[i][0], self.drone_pos[i][1]))
            else:
                self.drone_z[i] = max(ground_z_now, self.drone_z[i] - 2.5)
            
            # Map Drone Location
            dx, dy, dz = self.drone_pos[i][0], self.drone_pos[i][1], self.drone_z[i]
            self.drone_plots[i].set_data([dx], [dy])
            self.drone_plots[i].set_3d_properties([dz])
            
            # Draw ground shadow for realistic depth perception
            self.drone_shadows[i].set_data([dx, dx], [dy, dy])
            self.drone_shadows[i].set_3d_properties([ground_z_now, dz])
            
            x_start += self.curr_widths[i]

        # Camera Pan
        self.ax.view_init(elev=35, azim=-60 + (self.time * 0.8))

        status = f"SURVEY TEAM {len(self.active_drones)}/3"
        batt_str = f"BATT: D1:{self.batteries[0]:.0f}% | D2:{self.batteries[1]:.0f}% | D3:{self.batteries[2]:.0f}%"
        self.status_text.set_text(f"TIME: {self.time:.1f}s\nSTATUS: {status}\nPROGRESS: {self.area_scanned:.1f}%\nPATTERN: {self.patterns[self.pattern_idx]}\n{batt_str}")
        
        return self.drone_plots + self.drone_shadows + self.cam_images

sim = SwarmSim3D()
ani = animation.FuncAnimation(sim.fig, sim.update, frames=600, interval=50, blit=False)
plt.tight_layout()
plt.show()
