import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to path to allow importing webots_swarm module
sys.path.append('.')
from webots_swarm.swarm_3d_sim import SwarmSim3D

def save_frame():
    sim = SwarmSim3D()
    # Advance animation 50 frames so drones have moved into position
    for i in range(50):
        sim.update(i)
    
    # Save the generated UI to an image file
    output_path = '/Users/gary/.gemini/antigravity/brain/cef899f5-6551-4171-88af-906d38191714/ui_frame.png'
    sim.fig.savefig(output_path, dpi=120)
    print("SAVED_FRAME:", output_path)

if __name__ == "__main__":
    save_frame()
