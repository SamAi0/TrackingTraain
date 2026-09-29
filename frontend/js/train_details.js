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
        
        // Fix Leaflet map sizing issue after container becomes visible
        setTimeout(() => {
            if(window._leafletMap) window._leafletMap.resize();
        }, 200);
        
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
        
        const midPoint = validCoords[Math.floor(validCoords.length / 2)];
        const map = new maplibregl.Map({
            container: 'map',
            style: 'https://tiles.openfreemap.org/styles/positron',
            center: [midPoint.longitude, midPoint.latitude],
            zoom: 5
        });
        map.addControl(new maplibregl.NavigationControl(), 'top-right');
        window._leafletMap = map;
        
        const coords = [];
        
        map.on('load', () => {
            route.forEach((station, index) => {
                if (station.latitude && station.longitude) {
                    const isFirst = index === 0;
                    const isLast = index === route.length - 1;
                    
                    coords.push([station.longitude, station.latitude]);
                    
                    let markerColor = '#3388ff';
                    let radius = '12px';
                    
                    if (isFirst) {
                        markerColor = '#28a745';
                        radius = '16px';
                    } else if (isLast) {
                        markerColor = '#dc3545';
                        radius = '16px';
                    }
                    
                    const el = document.createElement('div');
                    el.style.backgroundColor = markerColor;
                    el.style.width = radius;
                    el.style.height = radius;
                    el.style.borderRadius = '50%';
                    el.style.border = '2px solid white';
                    el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
                    
                    const popupContent = `
                        <div class="text-center">
                            <strong>${station.station_name} (${station.station_code})</strong><br>
                            Seq: ${station.sequence_number}<br>
                            Arr: ${station.arrival_time || '--:--'} | Dep: ${station.departure_time || '--:--'}
                        </div>
                    `;
                    
                    new maplibregl.Marker({element: el})
                        .setLngLat([station.longitude, station.latitude])
                        .setPopup(new maplibregl.Popup({offset: 15}).setHTML(popupContent))
                        .addTo(map);
                }
            });
            
            if (coords.length > 1) {
                map.addSource('routeLine', {
                    'type': 'geojson',
                    'data': {
                        'type': 'Feature',
                        'properties': {},
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': coords
                        }
                    }
                });
                
                map.addLayer({
                    'id': 'routeLineLayer',
                    'type': 'line',
                    'source': 'routeLine',
                    'layout': {
                        'line-join': 'round',
                        'line-cap': 'round'
                    },
                    'paint': {
                        'line-color': '#f26422',
                        'line-width': 4,
                        'line-opacity': 0.8
                    }
                });
                
                const bounds = new maplibregl.LngLatBounds();
                coords.forEach(p => bounds.extend(p));
                map.fitBounds(bounds, {padding: 50});
            }
        });
    }
});
