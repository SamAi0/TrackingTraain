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
            
            setTimeout(() => {
                if (map) map.resize();
            }, 250);

            
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
        let isNew = false;
        if (!map) {
            map = new maplibregl.Map({
                container: 'map',
                style: 'https://tiles.openfreemap.org/styles/positron',
                center: [78.9629, 20.5937],
                zoom: 4
            });
            map.addControl(new maplibregl.NavigationControl(), 'top-right');
            isNew = true;
        }
        
        const route = data.route;
        const coords = [];
        const completedCoords = [];
        const upcomingCoords = [];
        
        let currentMarkerCoords = null;
        let currentStationName = data.current_station;
        
        route.forEach(stn => {
            if (stn.latitude && stn.longitude) {
                const coord = [stn.longitude, stn.latitude]; // MapLibre uses [lng, lat]
                coords.push(coord);
                
                if (stn.status === 'COMPLETED') {
                    completedCoords.push(coord);
                } else if (stn.status === 'UPCOMING') {
                    upcomingCoords.push(coord);
                } else if (stn.status === 'CURRENT') {
                    completedCoords.push(coord);
                    upcomingCoords.push(coord);
                    currentMarkerCoords = coord;
                }
            }
        });
        
        const drawLayers = () => {
            if (window._trainMarker) {
                window._trainMarker.remove();
            }
            
            // Completed Layer
            if (completedCoords.length > 1) {
                if (map.getSource('completedLine')) {
                    map.getSource('completedLine').setData({
                        'type': 'Feature',
                        'properties': {},
                        'geometry': { 'type': 'LineString', 'coordinates': completedCoords }
                    });
                } else {
                    map.addSource('completedLine', {
                        'type': 'geojson',
                        'data': {
                            'type': 'Feature',
                            'properties': {},
                            'geometry': { 'type': 'LineString', 'coordinates': completedCoords }
                        }
                    });
                    map.addLayer({
                        'id': 'completedLineLayer',
                        'type': 'line',
                        'source': 'completedLine',
                        'layout': { 'line-join': 'round', 'line-cap': 'round' },
                        'paint': { 'line-color': '#28a745', 'line-width': 5, 'line-opacity': 0.8 }
                    });
                }
            }
            
            // Upcoming Layer
            if (upcomingCoords.length > 1) {
                if (map.getSource('upcomingLine')) {
                    map.getSource('upcomingLine').setData({
                        'type': 'Feature',
                        'properties': {},
                        'geometry': { 'type': 'LineString', 'coordinates': upcomingCoords }
                    });
                } else {
                    map.addSource('upcomingLine', {
                        'type': 'geojson',
                        'data': {
                            'type': 'Feature',
                            'properties': {},
                            'geometry': { 'type': 'LineString', 'coordinates': upcomingCoords }
                        }
                    });
                    map.addLayer({
                        'id': 'upcomingLineLayer',
                        'type': 'line',
                        'source': 'upcomingLine',
                        'layout': { 'line-join': 'round', 'line-cap': 'round' },
                        'paint': { 'line-color': '#0dcaf0', 'line-width': 4, 'line-opacity': 0.6, 'line-dasharray': [2, 2] }
                    });
                }
            }
            
            if (currentMarkerCoords) {
                const el = document.createElement('div');
                el.innerHTML = `<div style="background-color: var(--accent-orange); color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(0,0,0,0.5); border: 2px solid white;">
                        <i class="bi bi-train-front" style="font-size: 16px;"></i>
                       </div>`;
                       
                window._trainMarker = new maplibregl.Marker({element: el.firstChild})
                    .setLngLat(currentMarkerCoords)
                    .setPopup(new maplibregl.Popup({offset: 15}).setHTML(`<strong>${currentStationName}</strong><br>Status: ${data.status.replace('_', ' ')}`))
                    .addTo(map);
                    
                map.flyTo({ center: currentMarkerCoords, zoom: 7 });
            } else if (coords.length > 0) {
                const bounds = new maplibregl.LngLatBounds();
                coords.forEach(p => bounds.extend(p));
                map.fitBounds(bounds, { padding: 50 });
            }
        };

        if (isNew) {
            map.on('load', drawLayers);
        } else {
            drawLayers();
        }
    }
});
