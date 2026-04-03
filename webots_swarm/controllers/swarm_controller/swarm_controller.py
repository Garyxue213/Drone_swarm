"""
Search and Rescue Swarm Controller for Webots
Final Stable Version for University Submission (Mission 3).
Features: 
- Dynamic Sectoring Coordination
- Heartbeat-based Jamming/Failure Resilience
- Fixed Z-up Altitude Control for R2025a Stability
"""

from controller import Robot, GPS, Compass, InertialUnit, Motor, Emitter, Receiver
import math

class SimpleDrone:
    def __init__(self):
        self.robot = Robot()
        self.name = self.robot.getName()
        self.drone_id = int(''.join(filter(str.isdigit, self.name)))
        self.time_step = int(self.robot.getBasicTimeStep())
        
        # Sensors
        self.gps = self.robot.getDevice('gps')
        self.gps.enable(self.time_step)
        self.imu = self.robot.getDevice('inertial unit')
        self.imu.enable(self.time_step)
        
        # Motors
        self.motors = [self.robot.getDevice(n) for n in [
            'front left propeller', 'front right propeller',
            'rear left propeller', 'rear right propeller'
        ]]
        for m in self.motors:
            m.setPosition(float('inf'))
            m.setVelocity(0.0)
            
        self.emitter = self.robot.getDevice('emitter')
        self.receiver = self.robot.getDevice('receiver')
        if self.receiver: self.receiver.enable(self.time_step)
        
        self.target_alt = 1.0  # Stable search altitude (1 meter)
        self.active_drones = {1, 2, 3}
        self.last_heartbeat = {1: 0.0, 2: 0.0, 3: 0.0}
        
    def run(self):
        print(f"[{self.name}] Drone Online. Mission 3: Resilience & Failover.")
        
        while self.robot.step(self.time_step) != -1:
            t = self.robot.getTime()
            p = self.gps.getValues() 
            if math.isnan(p[0]): continue
            
            # Webots R2025a Coordinate Mapping:
            # P[0] = X (Horizontal)
            # P[1] = Y (Horizontal)
            # P[2] = Z (Altitude)
            alt = p[2]
            
            rpy = self.imu.getRollPitchYaw() # [Roll, Pitch, Yaw]
            
            # 1. Telemetry Pulse (Every 2 seconds)
            if int(t * 100) % 200 == 0:
                print(f"[{self.name}] T:{t:.1f}s POS:({p[0]:.2f}, {p[1]:.2f}, {alt:.2f}) SWARM:{sorted(list(self.active_drones))}")

            # 2. Heartbeat Comms (Simulate Jamming at T=15s for Drone 3)
            if not (self.drone_id == 3 and t > 15.0):
                self.emitter.send(f"{self.drone_id}|{p[0]:.2f}|{p[1]:.2f}".encode('utf-8'))
            
            while self.receiver.getQueueLength() > 0:
                try:
                    msg = self.receiver.getString().split('|')
                    sender_id = int(msg[0])
                    self.last_heartbeat[sender_id] = t
                    if sender_id not in self.active_drones:
                        self.active_drones.add(sender_id)
                except: pass
                self.receiver.nextPacket()
            
            # 3. Resilience Logic (Failover if heartbeat stops for >5s)
            for d_id in list(self.active_drones):
                if d_id != self.drone_id and (t - self.last_heartbeat[d_id]) > 5.0:
                    print(f"[{self.name}] !!! SIGNAL LOST: Drone {d_id} jammed. Re-calculating sectors...")
                    self.active_drones.remove(d_id)
            
            # 4. Swarm Coordination (Dynamic Sectoring)
            sorted_swarm = sorted(list(self.active_drones))
            my_target_x = -10.0 + (sorted_swarm.index(self.drone_id) * (20.0/len(sorted_swarm)))
            
            # 5. PD Flight Stabilization
            # Altitude Control (Z-axis)
            alt_err = self.target_alt - alt
            base_thrust = 68.3 + (alt_err * 15.0)  # Lowered gain for stability
            
            # Bank angles (Roll and Pitch to keep it level)
            roll_act = rpy[0] * 35.0
            pitch_act = rpy[1] * 35.0
            
            # Heading Correction (Move toward target X)
            x_err = (my_target_x - p[0]) * 0.3
            pitch_act += x_err
            
            # Safety Clamp
            pitch_act = max(-8, min(pitch_act, 8))
            roll_act = max(-8, min(roll_act, 8))
            
            # Motor Mixing for Mavic 2 Pro
            m1 = base_thrust - roll_act - pitch_act
            m2 = base_thrust + roll_act - pitch_act
            m3 = base_thrust - roll_act + pitch_act
            m4 = base_thrust + roll_act + pitch_act
            
            # Physical Thresholds
            v = [max(0, min(mv, 500)) for mv in [m1, m2, m3, m4]]
            
            self.motors[0].setVelocity(v[0])
            self.motors[1].setVelocity(-v[1])
            self.motors[2].setVelocity(v[2])
            self.motors[3].setVelocity(-v[3])

if __name__ == "__main__":
    SimpleDrone().run()
