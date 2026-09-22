document.addEventListener('DOMContentLoaded', async () => {
    // Parse URL params
    const urlParams = new URLSearchParams(window.location.search);
    const trainNumber = urlParams.get('train');
    const sourceCode = urlParams.get('source');
    const destCode = urlParams.get('dest');
    
    const errorAlert = document.getElementById('errorAlert');
    const contentRow = document.getElementById('contentRow');
    const loadingHeader = document.getElementById('loadingHeader');
    const trainHeader = document.getElementById('trainHeader');
    const timelineContainer = document.getElementById('timelineContainer');
    
    if (!trainNumber) {
        showError("Invalid train selection. Please go back and search again.");
        return;
    }
    
    try {
        let apiUrl = `/api/trains/${trainNumber}/route/`;
        if (sourceCode && destCode) {
            apiUrl += `?source=${sourceCode}&destination=${destCode}`;
        }
        
        const res = await fetch(apiUrl);
        const data = await res.json();
        
        if (!res.ok) throw new Error(data.error || "Failed to load train details.");
        
        renderHeader(data);
        renderTimeline(data.route);
        initMap(data.route);
        
        loadingHeader.classList.add('d-none');
        trainHeader.classList.remove('d-none');
        contentRow.style.display = 'flex';
        
    } catch (err) {
        loadingHeader.classList.add('d-none');
        showError(err.message);
    }
    
    function showError(msg) {
        errorAlert.textContent = msg;
        errorAlert.classList.remove('d-none');
    }
    
    function renderHeader(data) {
        document.getElementById('trainTitle').textContent = `${data.train_number} - ${data.train_name}`;
        document.getElementById('trainType').textContent = data.train_type || 'EXPRESS';
        document.getElementById('trainSource').textContent = data.source || data.route[0].station_name;
        document.getElementById('trainDest').textContent = data.destination || data.route[data.route.length - 1].station_name;
    }
    
    function renderTimeline(route) {
        timelineContainer.innerHTML = '';
        
        route.forEach((station, index) => {
            const isFirst = index === 0;
            const isLast = index === route.length - 1;
            
            let timelineClass = 'timeline-item';
            if (isFirst) timelineClass += ' source';
            if (isLast) timelineClass += ' destination';
            
            const arr = station.arrival_time ? station.arrival_time : '--:--';
            const dep = station.departure_time ? station.departure_time : '--:--';
            const halt = station.halt_duration ? `<span class="badge bg-secondary ms-2">${station.halt_duration} halt</span>` : '';
            
            const item = document.createElement('div');
            item.className = timelineClass;
            item.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <div>
                        <span class="station-name">${station.station_name}</span>
                        <span class="station-code ms-1">(${station.station_code})</span>
                    </div>
                    <span class="badge bg-light text-dark border">Day ${station.day || 1}</span>
                </div>
                <div class="row gx-2 align-items-center mt-2">
                    <div class="col-auto">
                        <small class="text-muted d-block">Arrival</small>
                        <span class="time-box ${!station.arrival_time ? 'opacity-50' : ''}">${arr}</span>
                    </div>
                    <div class="col-auto">
                        <small class="text-muted d-block">Departure</small>
                        <span class="time-box ${!station.departure_time ? 'opacity-50' : ''}">${dep}</span>
                    </div>
                    <div class="col-auto mt-3">
                        ${halt}
                    </div>
                </div>
            `;
            timelineContainer.appendChild(item);
        });
    }
    
    function initMap(route) {
        // Find valid coordinates to center the map
        const validCoords = route.filter(s => s.latitude !== null && s.longitude !== null);
        
        if (validCoords.length === 0) {
            document.getElementById('map').innerHTML = `
                <div class="h-100 d-flex flex-column justify-content-center align-items-center bg-light">
                    <i class="bi bi-map text-muted" style="font-size: 3rem;"></i>
                    <h5 class="text-muted mt-3">Map Data Unavailable</h5>
                    <p class="text-muted text-center px-4">Station coordinates are missing for this route.</p>
                </div>
            `;
            return;
        }
        
        // Initialize map centered roughly in the middle of the route
        const midPoint = validCoords[Math.floor(validCoords.length / 2)];
        const map = L.map('map').setView([midPoint.latitude, midPoint.longitude], 5);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        
        const latlngs = [];
        
        route.forEach((station, index) => {
            if (station.latitude && station.longitude) {
                const isFirst = index === 0;
                const isLast = index === route.length - 1;
                
                latlngs.push([station.latitude, station.longitude]);
                
                let markerColor = '#3388ff'; // Default blue
                let radius = 6;
                let fillOpacity = 0.8;
                
                if (isFirst) {
                    markerColor = '#28a745'; // Green
                    radius = 8;
                    fillOpacity = 1;
                } else if (isLast) {
                    markerColor = '#dc3545'; // Red
                    radius = 8;
                    fillOpacity = 1;
                }
                
                const marker = L.circleMarker([station.latitude, station.longitude], {
                    radius: radius,
                    color: '#fff',
                    weight: 2,
                    fillColor: markerColor,
                    fillOpacity: fillOpacity
                }).addTo(map);
                
                const popupContent = `
                    <div class="text-center">
                        <strong>${station.station_name} (${station.station_code})</strong><br>
                        Seq: ${station.sequence_number}<br>
                        Arr: ${station.arrival_time || '--:--'} | Dep: ${station.departure_time || '--:--'}
                    </div>
                `;
                marker.bindPopup(popupContent);
            } else {
                console.warn(`Missing coordinates for station: ${station.station_code}`);
            }
        });
        
        // Draw polyline connecting the stations
        if (latlngs.length > 1) {
            const polyline = L.polyline(latlngs, {
                color: '#f26422', // TrackEase orange
                weight: 4,
                opacity: 0.8,
                lineJoin: 'round'
            }).addTo(map);
            
            // Zoom the map to fit the polyline
            map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
        }
    }
});
