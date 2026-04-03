import simplekml
import numpy as np

# --- Real-World Anchoring (Hudson Yards Construction Site, NYC) ---
BASE_LAT = 40.7535
BASE_LON = -74.0010
DEG_PER_METER = 0.000009

GRID_SIZE = 100
FAILURE_TIME = 15

# Helper function to convert 100x100 internal metric grid to GPS Lon/Lat
def grid_to_gps(x_m, y_m):
    lon = BASE_LON + (x_m * DEG_PER_METER)
    lat = BASE_LAT + (y_m * DEG_PER_METER)
    return [lon, lat]

class Building:
    def __init__(self, x, y, w, h, z, color, name):
        self.x, self.y, self.w, self.h, self.z = x, y, w, h, z
        self.color = color # KML uses hex but we'll use simplekml colors
        self.name = name

def run_simulation_to_kml(output_filename="drone_survey.kml"):
    print("[SYSTEM] Aggregating Swarm Mathematics into Google Earth Data...")
    kml = simplekml.Kml()
    
    # 1. ADD CONSTRUCTION BUILDINGS
    buildings = [
        Building(10, 20, 20, 30, 45, simplekml.Color.gray, 'Concrete Base'),
        Building(40, 45, 25, 25, 80, simplekml.Color.orange, 'Steel Scaffold'),
        Building(70, 10, 20, 40, 110, simplekml.Color.dimgray, 'Main Tower Core'),
        Building(20, 70, 15, 15, 25, simplekml.Color.red, 'Brick Stack'),
        Building(80, 70, 15, 20, 15, simplekml.Color.darkslategray, 'Equip. Depot'),
        Building(5, 5, 25, 10, 10, simplekml.Color.white, 'Trailer Office')
    ]
    
    # Create Ground Plane/Site Boundary (100x100m)
    p0 = grid_to_gps(0, 0)
    p1 = grid_to_gps(100, 0)
    p2 = grid_to_gps(100, 100)
    p3 = grid_to_gps(0, 100)
    site = kml.newpolygon(name="Construction Site Boundary",
                          outerboundaryis=[(p0[0], p0[1]), (p1[0], p1[1]), (p2[0], p2[1]), (p3[0], p3[1]), (p0[0], p0[1])])
    site.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.darkkhaki)
    
    # Generate 3D Extruded Buildings in KML
    b_folder = kml.newfolder(name="Construction Structures")
    for b in buildings:
        # 4 corners
        bl = grid_to_gps(b.x, b.y)
        br = grid_to_gps(b.x + b.w, b.y)
        tr = grid_to_gps(b.x + b.w, b.y + b.h)
        tl = grid_to_gps(b.x, b.y + b.h)
        
        # Extrude polygon
        pol = b_folder.newpolygon(name=b.name, extrude=1, altitudemode=simplekml.AltitudeMode.relativetoground)
        # KML polygons require coordinates as (lon, lat, alt)
        pol.outerboundaryis = [
            (bl[0], bl[1], b.z), (br[0], br[1], b.z), 
            (tr[0], tr[1], b.z), (tl[0], tl[1], b.z), (bl[0], bl[1], b.z)
        ]
        pol.style.polystyle.color = simplekml.Color.changealphaint(200, b.color)

    # 2. SIMULATE FLIGHT LOGIC
    def get_ground_elevation(x, y):
        # Extremely simplified heatmap extraction logic for the script
        z = 0
        for bd in buildings:
            if bd.x <= x <= bd.x + bd.w and bd.y <= y <= bd.y + bd.h:
                z = max(z, bd.z)
        return z

    active_drones = [0, 1, 2]
    drone_pos = [[10, 10], [50, 10], [80, 10]]
    drone_z = [15.0, 15.0, 15.0]
    curr_widths = [GRID_SIZE/3] * 3
    
    # Store path arrays for all 3 drones
    drone_paths = [[], [], []]
    
    FRAMES = 500
    print("[SYSTEM] Simulating 500 frames of Dynamic Re-allocation Pathing...")
    
    for frame in range(FRAMES):
        time = frame / 10.0
        
        # Sim Equipment failure drop out
        if time > FAILURE_TIME and 2 in active_drones:
            active_drones.remove(2)
        
        target_widths = [GRID_SIZE/2, GRID_SIZE/2, 0] if 2 not in active_drones else [GRID_SIZE/3] * 3
        for i in range(3):
            curr_widths[i] += (target_widths[i] - curr_widths[i]) * 0.1
        
        x_start = 0
        for i in range(3):
            if i in active_drones:
                # Zig-Zag logic
                target_x = x_start + curr_widths[i]/2 + (curr_widths[i]/2.5) * np.sin(time * 2 + i)
                drone_pos[i][0] += (target_x - drone_pos[i][0]) * 0.2
                drone_pos[i][1] = (drone_pos[i][1] + 1.2) % GRID_SIZE # Fast vertical sweep

                # Altimeter Tracking
                drone_z[i] += ((get_ground_elevation(drone_pos[i][0], drone_pos[i][1]) + 25) - drone_z[i]) * 0.2
            else:
                 drone_z[i] = max(0, drone_z[i] - 1.5) # RTB drop to 0
            
            # Save GPS data tuple
            gps = grid_to_gps(drone_pos[i][0], drone_pos[i][1])
            drone_paths[i].append((gps[0], gps[1], drone_z[i]))
            
            x_start += curr_widths[i]

    # 3. WRITE DRONE FLIGHT PATHS TO KML
    names = ["Alpha (D1)", "Bravo (D2)", "Charlie (D3)"]
    path_colors = [simplekml.Color.blue, simplekml.Color.green, simplekml.Color.red]
    
    flight_folder = kml.newfolder(name="Swarm Survey Pathing (Z-Elevation)")
    for i in range(3):
        lin = flight_folder.newlinestring(name=names[i] + " Flight Path", 
                                          altitudemode=simplekml.AltitudeMode.relativetoground,
                                          extrude=1)
        lin.coords = drone_paths[i]
        lin.style.linestyle.color = path_colors[i]
        lin.style.linestyle.width = 4
        # Makes the drop-shadow wall translucent
        lin.style.polystyle.color = simplekml.Color.changealphaint(80, path_colors[i]) 
        
    kml.save(output_filename)
    print(f"[SUCCESS] Exported Google Earth 3D Simulation to {output_filename}")
    print("[INSTRUCTION] Double click the file or drag it into Google Earth Web to view the realism!")

if __name__ == "__main__":
    run_simulation_to_kml()
