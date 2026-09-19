document.addEventListener('DOMContentLoaded', () => {
    const fromSelect = document.getElementById('from-station');
    const toSelect = document.getElementById('to-station');
    const swapBtn = document.getElementById('swap-btn');
    const findRouteBtn = document.getElementById('find-route-btn');
    const resultsSection = document.getElementById('results-section');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('error-message');
    const trainsContainer = document.getElementById('trains-container');
    const timelineContainer = document.getElementById('timeline-container');
    const trainsList = document.getElementById('trains-list');
    const timeline = document.getElementById('timeline');
    const timelineTitle = document.getElementById('timeline-title');
    const statDist = document.getElementById('stat-dist');
    const statStops = document.getElementById('stat-stops');

    // List of major Maharashtra stations for the demo
    const maharashtraStations = [
        { code: 'CSTM', name: 'Chhatrapati Shivaji Maharaj Terminus' },
        { code: 'TNA', name: 'Thane' },
        { code: 'KYN', name: 'Kalyan Junction' },
        { code: 'PNVL', name: 'Panvel' },
        { code: 'PUNE', name: 'Pune Junction' },
        { code: 'NGP', name: 'Nagpur' },
        { code: 'NK', name: 'Nashik Road' },
        { code: 'BSL', name: 'Bhusaval Junction' },
        { code: 'SUR', name: 'Solapur' },
        { code: 'KOP', name: 'Kolhapur CSMT' },
        { code: 'AK', name: 'Akola Junction' },
        { code: 'BD', name: 'Badnera Junction' }
    ];

    // Populate dropdowns
    function populateDropdowns() {
        maharashtraStations.forEach(stn => {
            const option1 = new Option(`${stn.name} (${stn.code})`, stn.code);
            const option2 = new Option(`${stn.name} (${stn.code})`, stn.code);
            fromSelect.add(option1);
            toSelect.add(option2);
        });
    }

    populateDropdowns();

    // Swap stations
    swapBtn.addEventListener('click', () => {
        const temp = fromSelect.value;
        fromSelect.value = toSelect.value;
        toSelect.value = temp;
    });

    // Find Route
    findRouteBtn.addEventListener('click', async () => {
        const fromCode = fromSelect.value;
        const toCode = toSelect.value;

        if (!fromCode || !toCode) {
            alert('Please select both Origin and Destination stations.');
            return;
        }
        
        if (fromCode === toCode) {
            alert('Origin and Destination cannot be the same.');
            return;
        }

        // Show loading state
        resultsSection.classList.remove('hidden');
        loader.classList.remove('hidden');
        errorMessage.classList.add('hidden');
        trainsContainer.classList.add('hidden');
        timelineContainer.classList.add('hidden');

        try {
            const response = await fetch(`/api/routes/trains/?from=${fromCode}&to=${toCode}`);
            const data = await response.json();

            if (!response.ok || !data.trains || data.trains.length === 0) {
                throw new Error('No routes found');
            }

            renderTrains(data.trains, fromCode, toCode);
        } catch (error) {
            loader.classList.add('hidden');
            errorMessage.classList.remove('hidden');
        }
    });

    function renderTrains(trains, fromCode, toCode) {
        trainsList.innerHTML = '';
        loader.classList.add('hidden');
        trainsContainer.classList.remove('hidden');

        trains.forEach((train, index) => {
            const card = document.createElement('div');
            card.className = 'train-card';
            
            // Format days
            let daysText = 'All Days';
            if (train.running_days) {
                const activeDays = Object.keys(train.running_days).filter(d => train.running_days[d]);
                if (activeDays.length < 7) {
                    daysText = activeDays.map(d => d.substring(0, 3)).join(', ');
                }
            }

            card.innerHTML = `
                <div class="train-info">
                    <div class="train-title"><span>🚆</span> ${train.train_number} - ${train.train_name}</div>
                    <div class="train-stats">
                        <span>Dep: ${train.departure || '--:--'}</span>
                        <span>Arr: ${train.arrival || '--:--'}</span>
                        <span>Dist: ${train.distance_km} KM</span>
                        <span>Days: ${daysText}</span>
                    </div>
                </div>
                <button class="view-route-btn" data-train="${train.train_number}">View Timeline</button>
            `;
            trainsList.appendChild(card);
        });

        // Add event listeners to view route buttons
        document.querySelectorAll('.view-route-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const trainNum = e.target.getAttribute('data-train');
                fetchRouteTimeline(trainNum, fromCode, toCode);
            });
        });
        
        // Automatically load timeline for first train
        if (trains.length > 0) {
            fetchRouteTimeline(trains[0].train_number, fromCode, toCode);
        }
    }

    async function fetchRouteTimeline(trainNum, fromCode, toCode) {
        try {
            const response = await fetch(`/api/routes/search/?from=${fromCode}&to=${toCode}&train=${trainNum}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error('Could not generate timeline');
            }

            renderTimeline(data);
        } catch (error) {
            console.error(error);
        }
    }

    function renderTimeline(data) {
        timelineContainer.classList.remove('hidden');
        timelineTitle.textContent = `${data.source || data.from} → ${data.destination || data.to}`;
        statDist.textContent = `${data.total_distance_km} KM`;
        statStops.textContent = data.route_type === 'multi_train' ? `${data.transfers} TRANSFERS` : `${data.station_count} STATIONS`;

        timeline.innerHTML = '';

        if (data.route_type === 'multi_train') {
            data.segments.forEach(seg => {
                if (seg.type === 'train') {
                    // Render train header
                    const header = document.createElement('div');
                    header.className = 'timeline-item';
                    header.innerHTML = `
                        <div class="station-info">
                            <div class="station-name">🚆 Train ${seg.train_number}</div>
                            <div class="station-meta">${seg.from} to ${seg.to} • ${seg.distance_km} KM</div>
                        </div>
                    `;
                    timeline.appendChild(header);

                    seg.stops.forEach(stn => {
                        const item = document.createElement('div');
                        item.className = 'timeline-item';
                        item.innerHTML = renderStationTimelineItem(stn);
                        timeline.appendChild(item);
                    });
                } else if (seg.type === 'transfer') {
                    const item = document.createElement('div');
                    item.className = 'timeline-item';
                    item.innerHTML = `
                        <div class="station-info">
                            <div class="station-name" style="color: var(--accent);">🔄 CHANGE TRAIN AT ${seg.station}</div>
                            <div class="station-meta">Arrival: ${seg.arrival_time || 'Not Available'} • Next Departure: ${seg.next_departure_time || 'Not Available'}</div>
                        </div>
                    `;
                    timeline.appendChild(item);
                }
            });
        } else {
            // Direct train
            data.stations.forEach(stn => {
                const item = document.createElement('div');
                item.className = 'timeline-item';
                item.innerHTML = renderStationTimelineItem(stn);
                timeline.appendChild(item);
            });
        }
        
        timelineContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function renderStationTimelineItem(stn) {
        const arr = stn.arrival_time ? `<span class="time-label">Arr</span><span class="time">${stn.arrival_time}</span>` : '<span class="time-label">Arr</span><span class="time" style="font-size:12px">Not Available</span>';
        const dep = stn.departure_time ? `<span class="time-label">Dep</span><span class="time">${stn.departure_time}</span>` : '<span class="time-label">Dep</span><span class="time" style="font-size:12px">Not Available</span>';
        
        return `
            <div class="station-info">
                <div class="station-name">${stn.station_name} (${stn.station_code})</div>
                <div class="station-meta">${stn.distance_from_start} KM • Day ${stn.journey_day}</div>
            </div>
            <div class="station-times">
                ${arr}
                ${dep}
            </div>
        `;
    }
});
