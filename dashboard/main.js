const mapContainer = document.getElementById('map-view');
const baseMap = document.getElementById('base-map');
let currentX = 0;
let currentY = 0;
let isDragging = false;
let startX, startY;

// Setup Drag & Pan
mapContainer.addEventListener('mousedown', (e) => {
  isDragging = true;
  startX = e.clientX - currentX;
  startY = e.clientY - currentY;
  mapContainer.style.cursor = 'grabbing';
});

window.addEventListener('mouseup', () => {
  isDragging = false;
  mapContainer.style.cursor = 'grab';
});

window.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  currentX = e.clientX - startX;
  currentY = e.clientY - startY;
  
  currentX = Math.max(-500, Math.min(500, currentX));
  currentY = Math.max(-500, Math.min(500, currentY));
  
  baseMap.style.transform = `translate(${currentX}px, ${currentY}px) scale(1.1)`;
  updateDronePositionsOnMap();
});

// Drone Data & UI Elements
let dronesData = [];
const markers = {
  d1: document.getElementById('marker-d1'),
  d2: document.getElementById('marker-d2'),
  d3: document.getElementById('marker-d3')
};
const povs = {
  d1: document.getElementById('pov-d1'),
  d2: document.getElementById('pov-d2'),
  d3: document.getElementById('pov-d3')
};
const log = document.getElementById('console-log');

function logEvent(msg, isError=false) {
  const d = new Date();
  const t = `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}:${String(d.getSeconds()).padStart(2,'0')}`;
  const p = document.createElement('p');
  if(isError) p.className = 'error';
  p.innerText = `[${t}] ${msg}`;
  log.appendChild(p);
  log.scrollTop = log.scrollHeight;
}

// Map drone positions accounting for pan
function updateDronePositionsOnMap() {
  dronesData.forEach(d => {
    if (markers[d.id]) {
      markers[d.id].style.left = `${d.x}%`;
      markers[d.id].style.top = `${d.y}%`;
      markers[d.id].style.transform = `translate(calc(-50% + ${currentX}px), calc(-50% + ${currentY}px))`;
    }
  });

  if (dronesData.length > 0 && dronesData[0].fire_active) {
    const fw = document.getElementById('wrapper-fire');
    const fb = document.getElementById('fire-banner');
    if (fw) {
      fw.style.display = 'block';
      fw.style.left = `${dronesData[0].fire_pos_x}%`;
      fw.style.top = `${dronesData[0].fire_pos_y}%`;
      fw.style.transform = `translate(calc(-50% + ${currentX}px), calc(-50% + ${currentY}px))`;
    }
    if (fb) fb.style.display = 'block';
  } else {
    const fw = document.getElementById('wrapper-fire');
    const fb = document.getElementById('fire-banner');
    if (fw) fw.style.display = 'none';
    if (fb) fb.style.display = 'none';
  }
}

// WebSocket Connection to Python Backend
let activeWs = null;

function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8765');
  activeWs = ws;
  
  ws.onopen = () => {
    logEvent("CONNECTED to Python Simulation Server.");
    document.querySelector('.dot').style.backgroundColor = '#10b981';
  };
  
  ws.onclose = () => {
    logEvent("DISCONNECTED from Server.", true);
    document.querySelector('.dot').style.backgroundColor = '#ef4444';
    setTimeout(connectWebSocket, 5000);
  };
  
  ws.onmessage = (event) => {
    dronesData = JSON.parse(event.data);
    updateDronePositionsOnMap();
    
    dronesData.forEach(d => {
      // Update Telemetry sidebar
      const altEl = document.getElementById(`${d.id}-alt`);
      const secEl = document.getElementById(`${d.id}-sec`);
      const card = document.getElementById(`card-${d.id}`);
      const battEl = card.querySelector('.battery');
      
      if(altEl) altEl.innerText = `${d.z.toFixed(1)}m`;
      if(secEl) secEl.innerText = d.sector;
      if(battEl) {
        battEl.innerText = `${d.battery.toFixed(0)}%`;
        if (d.battery < 20) battEl.className = 'battery low';
        else battEl.className = 'battery';
      }
      
      if(d.status !== "ACTIVE" && d.status !== "RESPONDING") {
        card.style.opacity = '0.5';
        if (markers[d.id]) markers[d.id].classList.add("rtl-mode");
        
        if (d.status === "GPS ANOMALY") {
          card.classList.add("highlight-red");
          if (markers[d.id]) markers[d.id].classList.add("gps-anomaly");
        } else {
          card.classList.remove("highlight-red");
          if (markers[d.id]) markers[d.id].classList.remove("gps-anomaly");
        }
      } else {
        card.style.opacity = '1';
        card.classList.remove("highlight-red");
        if (markers[d.id]) {
          markers[d.id].classList.remove("rtl-mode");
          markers[d.id].classList.remove("gps-anomaly");
        }
      }
      
      // Update POV Camera
      if (povs[d.id]) {
        if(d.status === "ACTIVE" || d.status === "RESPONDING") {
          // Dynamic crop of the map.png representing the ground beneath it
          const bgX = d.x; 
          const bgY = d.y;
          povs[d.id].style.backgroundPosition = `${bgX}% ${bgY}%`;
          povs[d.id].classList.remove("offline");
          document.getElementById(`pov-alt-${d.id}`).innerText = `ALT: ${d.z.toFixed(1)}m`;
          
          if (d.id === "d1") {
            const povFire = document.getElementById("pov-d1-fire");
            if (povFire) {
              if (d.fire_active && Math.abs(d.x - d.fire_pos_x) < 5 && Math.abs(d.y - d.fire_pos_y) < 5) {
                povFire.style.display = 'block';
              } else {
                povFire.style.display = 'none';
              }
            }
          }
        } else {
          povs[d.id].classList.add("offline");
          document.getElementById(`pov-alt-${d.id}`).innerText = d.status;
          if (d.id === "d1") {
            const povFire = document.getElementById("pov-d1-fire");
            if (povFire) povFire.style.display = 'none';
          }
        }
      }
      // Update Hacker Terminal (Bonus: Eavesdropping Case)
      const hackerTerm = document.getElementById('hacker-terminal');
      if (hackerTerm) {
        const p = document.createElement('div');
        p.className = 'packet-intercept';
        p.innerText = `[RECV] ${JSON.stringify(dronesData).substring(0, 80)}...`;
        hackerTerm.appendChild(p);
        if (hackerTerm.childNodes.length > 15) hackerTerm.removeChild(hackerTerm.firstChild);
        hackerTerm.scrollTop = hackerTerm.scrollHeight;
      }
    });
  };
}

// Hacker Injection Logic
document.getElementById('btn-inject-fire').addEventListener('click', () => {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify({ command: 'fire' }));
    logEvent("PACKET INJECTION: FORCED FIRE ALERT", true);
  }
});

document.getElementById('btn-inject-spoof').addEventListener('click', () => {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify({ command: 'spoof' }));
    logEvent("PACKET INJECTION: GPS OFFSET OVERRIDE", true);
  }
});

document.getElementById('btn-refresh').addEventListener('click', () => {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify({ command: 'refresh' }));
    logEvent("Refresh Mission command sent.");
  }
});

document.getElementById('btn-rtl').addEventListener('click', () => {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify({ command: 'rtl' }));
    logEvent("Emergency RTL command sent.", true);
  }
});

document.getElementById('btn-fire').addEventListener('click', () => {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify({ command: 'fire' }));
    logEvent("🔥 Fire Alert injected!", true);
  }
});

document.getElementById('btn-spoof').addEventListener('click', () => {
  if (activeWs && activeWs.readyState === WebSocket.OPEN) {
    activeWs.send(JSON.stringify({ command: 'spoof' }));
    logEvent("🛰️ GPS Spoofing Attack Injected!", true);
  }
});

connectWebSocket();
