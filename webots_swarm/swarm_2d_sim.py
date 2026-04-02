import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# --- Swarm Configuration ---
GRID_SIZE = 100
DRONES = ["Alpha (D1)", "Bravo (D2)", "Charlie (D3)"]
COLORS = ["#3498db", "#2ecc71", "#e74c3c"] # Modern Blue, Green, Red
FAILURE_TIME = 15  # Seconds until D3 "Jamming" occurs

class SwarmSim2D:
    def __init__(self):
        plt.style.use('dark_background')
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.set_xlim(0, GRID_SIZE)
        self.ax.set_ylim(0, GRID_SIZE)
        self.ax.set_title("Mission 3: Swarm Resilience (Logic Visualization)", fontsize=14, pad=20)
        
        # Grid Styling
        self.ax.grid(color='white', alpha=0.1)
        self.ax.set_facecolor('#1e1e1e')
        
        # UI Elements
        self.drone_plots = [self.ax.plot([], [], 'o', color=c, markersize=12, label=n, 
                            markeredgecolor='white', markeredgewidth=1)[0] 
                            for n, c in zip(DRONES, COLORS)]
        
        # Sector Rectangles
        self.sector_rects = [plt.Rectangle((0, 0), 0, 0, alpha=0.15, color=c) 
                             for c in COLORS]
        for r in self.sector_rects: self.ax.add_patch(r)
        
        # HUD Text
        self.status_text = self.ax.text(2, 95, "", color='white', fontsize=12, verticalalignment='top')
        self.alert_text = self.ax.text(50, 50, "", color='red', fontsize=20, 
                                       weight='bold', horizontalalignment='center', alpha=0)
        
        # State
        self.time = 0
        self.active_drones = [0, 1, 2]
        self.drone_pos = [[10, 10], [50, 10], [80, 10]]
        self.target = [25, 60] # Target hidden in Alpha's new expanded sector
        self.target_found = False
        
        # Smooth Sector Resize State
        self.curr_widths = [GRID_SIZE/3] * 3
        self.target_widths = [GRID_SIZE/3] * 3
        
        self.frame_offset = 0
        self.current_frame = 0
        self.target_enabled = True
        self.batteries = [100.0, 100.0, 100.0]
        self.patterns = ["Vertical Sweep", "Zig-Zag", "Circular Patrol"]
        self.pattern_idx = 0
        
        # Plot Target (Invisible until found)
        self.target_plot, = self.ax.plot(self.target[0], self.target[1], 'x', color='yellow', markersize=15, alpha=0)
        self.ax.legend(loc='lower right', frameon=True, facecolor='black')
        
        # Keyboard Listener
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.ax.text(2, 2, "Controls: [P] Change Pattern | [H] Hide Target | [R] Restart | [B] Drain D1", color='gray', fontsize=10)
        
    def on_key_press(self, event):
        if event.key == 'h':
            self.target_enabled = not self.target_enabled
            if self.target_enabled:
                self.target = [25, 60]
                print("[SYSTEM] Target Enabled (Will be found at T=25s)")
            else:
                self.target = [-1000, -1000] # Hide target
                print("[SYSTEM] Target Hidden (100% Coverage Mode)")
            
            self.target_plot.set_data([self.target[0]], [self.target[1]])
            if self.target_found and not self.target_enabled:
                self.target_found = False
                self.target_plot.set_alpha(0)
                
        elif event.key == 'r':
            print("[SYSTEM] Restarting Simulation")
            self.frame_offset += self.current_frame
            self.time = 0
            self.active_drones = [0, 1, 2]
            self.drone_pos = [[10, 10], [50, 10], [80, 10]]
            self.target_found = False
            self.target_plot.set_alpha(0)
            self.curr_widths = [GRID_SIZE/3] * 3
            self.target_widths = [GRID_SIZE/3] * 3
            self.alert_text.set_alpha(0)
            for i, dp in enumerate(self.drone_plots):
                dp.set_color(COLORS[i])
                dp.set_alpha(1.0)
            self.batteries = [100.0, 100.0, 100.0]
            
        elif event.key == 'b':
            if 0 in self.active_drones:
                self.batteries[0] = 14.9
                print("[SYSTEM] Battery Drain Triggered! Alpha (D1) at critical battery.")
                
        elif event.key == 'p':
            self.pattern_idx = (self.pattern_idx + 1) % len(self.patterns)
            print(f"[SYSTEM] Switched Flight Pattern to: {self.patterns[self.pattern_idx]}")

    def update(self, frame):
        self.current_frame = frame - self.frame_offset
        self.time = self.current_frame / 10.0  # 10 FPS
        
        # Battery Logic (Step 6)
        for i in list(self.active_drones):
            self.batteries[i] -= 0.05
            if self.batteries[i] < 15.0:
                print(f"[SYSTEM] {DRONES[i]} hit 15% Battery. Returning Home.")
                self.active_drones.remove(i)
                rem = len(self.active_drones)
                if rem > 0:
                    for j in range(3):
                        self.target_widths[j] = GRID_SIZE / rem if j in self.active_drones else 0
                self.alert_text.set_text(f"!!! {DRONES[i]} LOW BATTERY - RTB !!!")
                self.alert_text.set_alpha(1.0)
                self.drone_plots[i].set_color('#333333')
                self.drone_plots[i].set_alpha(0.5)
        
        # 1. Jamming Attack Logic
        if self.time > FAILURE_TIME and 2 in self.active_drones:
            self.active_drones.remove(2)
            self.target_widths = [GRID_SIZE/2, GRID_SIZE/2, 0] # Re-allocate
            self.alert_text.set_text("!!! JAMMING ATTACK DETECTED !!!")
            self.alert_text.set_alpha(1.0)
        
        # Fade out alert after 3 seconds
        if self.time > FAILURE_TIME + 3:
            curr_alpha = self.alert_text.get_alpha()
            if curr_alpha > 0: self.alert_text.set_alpha(max(0, curr_alpha - 0.05))

        # 2. Smoothly Animate Sector Widths (Interpolation)
        for i in range(3):
            self.curr_widths[i] += (self.target_widths[i] - self.curr_widths[i]) * 0.1
        
        # 3. Update Visuals
        x_start = 0
        for i in range(3):
            # Update Rectangle
            self.sector_rects[i].set_xy((x_start, 0))
            self.sector_rects[i].set_width(self.curr_widths[i])
            self.sector_rects[i].set_height(GRID_SIZE)
            
            # Movement Logic
            if i in self.active_drones:
                if self.target_found:
                    # Hover above target
                    offsets = [[0, 5], [-5, -5], [5, -5]]
                    target_x = self.target[0] + offsets[i][0]
                    target_y = self.target[1] + offsets[i][1]
                    self.drone_pos[i][0] += (target_x - self.drone_pos[i][0]) * 0.1
                    self.drone_pos[i][1] += (target_y - self.drone_pos[i][1]) * 0.1
                else:
                    # Search Patterns
                    pattern = self.patterns[self.pattern_idx]
                    
                    if pattern == "Vertical Sweep":
                        target_x = x_start + self.curr_widths[i]/2
                        self.drone_pos[i][0] += (target_x - self.drone_pos[i][0]) * 0.1
                        self.drone_pos[i][1] = (self.drone_pos[i][1] + 1) % GRID_SIZE
                        
                    elif pattern == "Zig-Zag":
                        # Sine wave oscillating across the sector width
                        target_x = x_start + self.curr_widths[i]/2 + (self.curr_widths[i]/2.5) * np.sin(self.time * 2 + i)
                        self.drone_pos[i][0] += (target_x - self.drone_pos[i][0]) * 0.1
                        self.drone_pos[i][1] = (self.drone_pos[i][1] + 0.8) % GRID_SIZE
                        
                    elif pattern == "Circular Patrol":
                        # Cosine/Sine based circular loops constrained to sector
                        target_x = x_start + self.curr_widths[i]/2 + (self.curr_widths[i]/2.5) * np.cos(self.time * 2 + i)
                        target_y = 50 + 40 * np.sin(self.time * 2 + i)
                        self.drone_pos[i][0] += (target_x - self.drone_pos[i][0]) * 0.1
                        self.drone_pos[i][1] += (target_y - self.drone_pos[i][1]) * 0.1
                    
                    # Target Detection Check
                    dist = np.sqrt((self.drone_pos[i][0]-self.target[0])**2 + (self.drone_pos[i][1]-self.target[1])**2)
                    if dist < 5 and not self.target_found:
                        self.target_found = True
                        self.target_plot.set_alpha(1.0)
                        print(f"[FOUND] Drone {DRONES[i]} detected target!")
            
            self.drone_plots[i].set_data([self.drone_pos[i][0]], [self.drone_pos[i][1]])
            x_start += self.curr_widths[i]

        # Drone 3 (Charlie) - Static when jammed
        if 2 not in self.active_drones:
            self.drone_plots[2].set_color('#555555') # Gray
            self.drone_plots[2].set_alpha(0.5)

        # 4. Update HUD
        status = f"SWARM {len(self.active_drones)}/3"
        found_txt = " | TARGET: FOUND!" if self.target_found else ""
        batt_str = f"BATT: D1:{self.batteries[0]:.0f}% D2:{self.batteries[1]:.0f}% D3:{self.batteries[2]:.0f}%"
        self.status_text.set_text(f"TIME: {self.time:.1f}s\nSTATUS: {status}{found_txt}\nPATTERN: {self.patterns[self.pattern_idx]}\n{batt_str}")

        return self.drone_plots + self.sector_rects + [self.status_text, self.alert_text, self.target_plot]

sim = SwarmSim2D()
ani = animation.FuncAnimation(sim.fig, sim.update, frames=400, interval=50, blit=True)
plt.tight_layout()
plt.show()
