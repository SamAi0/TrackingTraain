document.addEventListener('DOMContentLoaded', () => {
    const trackForm = document.getElementById('trackForm');
    const trainInput = document.getElementById('trainInput');
    const delaySelect = document.getElementById('delaySelect');
    
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorAlert = document.getElementById('errorAlert');
    const contentRow = document.getElementById('contentRow');
    
    let map = null;
    let markersLayer = null;

    trackForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const trainNumber = trainInput.value.trim();
        const delay = delaySelect.value;
        
        if (!trainNumber) return;
        
        errorAlert.classList.add('d-none');
        contentRow.style.display = 'none';
        loadingIndicator.classList.remove('d-none');
        
        try {
            const res = await fetch(`/api/trains/${trainNumber}/track/?demo_delay=${delay}`);
            const data = await res.json();
            
            loadingIndicator.classList.add('d-none');
            
            if (!res.ok) throw new Error(data.error || 'Failed to track train');
            
            renderStatus(data);
            renderRouteProgress(data.route);
            initMap(data);
            
            contentRow.style.display = 'flex';
            
        } catch (err) {
            loadingIndicator.classList.add('d-none');
            errorAlert.textContent = err.message;
            errorAlert.classList.remove('d-none');
        }
    });
    
    function renderStatus(data) {
        document.getElementById('trainTitle').textContent = `${data.train_number} - ${data.train_name}`;
        
        const statusEl = document.getElementById('trainStatus');
        statusEl.textContent = data.status.replace('_', ' ');
        statusEl.className = `fs-5 status-${data.status}`;
        
        document.getElementById('prevStn').textContent = data.previous_station || '--';
        document.getElementById('currStn').textContent = data.current_station || '--';
        document.getElementById('nextStn').textContent = data.next_station || '--';
        
        document.getElementById('expArr').textContent = data.expected_arrival || '--:--';
        document.getElementById('expDep').textContent = data.expected_departure || '--:--';
        
        document.getElementById('progressBar').style.width = `${data.progress_percentage}%`;
        
        const d = new Date(data.last_updated);
        document.getElementById('lastUpdated').textContent = d.toLocaleTimeString();
    }
    
    function renderRouteProgress(route) {
        const container = document.getElementById('routeProgressContainer');
        container.innerHTML = '';
        
        let scrollToEl = null;
        
        route.forEach(stn => {
            const item = document.createElement('div');
            
            let statusClass = 'upcoming';
            if (stn.status === 'COMPLETED') statusClass = 'completed';
            if (stn.status === 'CURRENT') {
                statusClass = 'current';
                scrollToEl = item;
            }
            
            item.className = `route-item ${statusClass}`;
            
            const timeDisplay = stn.status === 'COMPLETED' 
                ? `<span class="time-box text-success">Dep: ${stn.expected_departure}</span>`
                : (stn.status === 'CURRENT' 
                    ? `<span class="time-box text-primary fw-bold">Exp: ${stn.expected_departure}</span>` 
                    : `<span class="time-box">Sch: ${stn.expected_arrival}</span>`);
            
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${stn.station_name}</strong>
                        <small class="text-muted ms-1">(${stn.station_code})</small>
                    </div>
                    ${timeDisplay}
                </div>
            `;
            
            container.appendChild(item);
        });
        
        if (scrollToEl) {
            setTimeout(() => {
                scrollToEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
        }
    }
    
    function initMap(data) {
        if (!map) {
            map = L.map('map');
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(map);
            markersLayer = L.layerGroup().addTo(map);
        } else {
            markersLayer.clearLayers();
        }
        
        const route = data.route;
        const latlngs = [];
        const completedLatlngs = [];
        const upcomingLatlngs = [];
        
        let currentMarkerCoords = null;
        let currentStationName = data.current_station;
        
        route.forEach(stn => {
            if (stn.latitude && stn.longitude) {
                const coord = [stn.latitude, stn.longitude];
                latlngs.push(coord);
                
                if (stn.status === 'COMPLETED') {
                    completedLatlngs.push(coord);
                } else if (stn.status === 'UPCOMING') {
                    upcomingLatlngs.push(coord);
                } else if (stn.status === 'CURRENT') {
                    completedLatlngs.push(coord); // connects previous to current
                    upcomingLatlngs.push(coord);  // connects current to next
                    currentMarkerCoords = coord;
                }
            }
        });
        
        // Draw completed segment (dark grey/green)
        if (completedLatlngs.length > 1) {
            L.polyline(completedLatlngs, {
                color: '#28a745',
                weight: 5,
                opacity: 0.8,
                lineJoin: 'round'
            }).addTo(markersLayer);
        }
        
        // Draw upcoming segment (blue/orange)
        if (upcomingLatlngs.length > 1) {
            L.polyline(upcomingLatlngs, {
                color: '#0dcaf0',
                weight: 4,
                opacity: 0.6,
                dashArray: '5, 10',
                lineJoin: 'round'
            }).addTo(markersLayer);
        }
        
        // Draw current train marker
        if (currentMarkerCoords) {
            const trainIcon = L.divIcon({
                className: 'custom-train-marker',
                html: `<div style="background-color: var(--accent-orange); color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(0,0,0,0.5); border: 2px solid white;">
                        <i class="bi bi-train-front" style="font-size: 16px;"></i>
                       </div>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });
            
            const marker = L.marker(currentMarkerCoords, { icon: trainIcon, zIndexOffset: 1000 }).addTo(markersLayer);
            marker.bindPopup(`<strong>${currentStationName}</strong><br>Status: ${data.status.replace('_', ' ')}`).openPopup();
            
            map.setView(currentMarkerCoords, 7);
        } else if (latlngs.length > 0) {
            map.fitBounds(L.polyline(latlngs).getBounds(), { padding: [50, 50] });
        }
    }
});
