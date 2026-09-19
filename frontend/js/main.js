document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('trainSearchForm');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const source = document.getElementById('sourceStation').value.trim();
            const dest = document.getElementById('destinationStation').value.trim();
            
            if (!source || !dest) return;
            
            // Show loading
            document.getElementById('loadingIndicator').classList.remove('d-none');
            document.getElementById('searchResults').classList.add('d-none');
            const resultsContainer = document.getElementById('resultsContainer');
            resultsContainer.innerHTML = '';
            
            // Fetch API
            fetch(`/api/trains/search/?source=${source}&dest=${dest}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('loadingIndicator').classList.add('d-none');
                    document.getElementById('searchResults').classList.remove('d-none');
                    
                    if (data.error) {
                        resultsContainer.innerHTML = `<div class="alert alert-danger w-100">${data.error}</div>`;
                        return;
                    }
                    
                    if (data.length === 0) {
                        resultsContainer.innerHTML = `
                            <div class="col-12 text-center py-5">
                                <i class="bi bi-calendar-x text-muted" style="font-size: 3rem;"></i>
                                <h4 class="mt-3 text-muted">No Trains Found</h4>
                                <p>We couldn't find any trains running between ${source.toUpperCase()} and ${dest.toUpperCase()}.</p>
                            </div>
                        `;
                        return;
                    }
                    
                    // Render Train Cards
                    data.forEach(train => {
                        const card = document.createElement('div');
                        card.className = 'col-md-6 col-lg-4';
                        card.innerHTML = `
                            <div class="card h-100 shadow-sm border-0 train-card">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <h5 class="card-title fw-bold text-primary mb-0">${train.number}</h5>
                                        <span class="badge bg-info text-dark rounded-pill">${train.train_type}</span>
                                    </div>
                                    <h6 class="card-subtitle mb-3 text-dark fw-semibold">${train.name}</h6>
                                    
                                    <div class="d-flex justify-content-between text-muted small mb-4">
                                        <div class="text-center">
                                            <i class="bi bi-geo-alt-fill text-danger d-block mb-1"></i>
                                            <span class="fw-bold d-block">${train.source.code}</span>
                                            <span style="font-size: 0.75rem;">${train.source.name}</span>
                                        </div>
                                        <div class="d-flex align-items-center flex-grow-1 px-3">
                                            <div class="border-bottom border-secondary border-2 flex-grow-1" style="border-style: dashed !important;"></div>
                                            <i class="bi bi-train-front ms-2 text-secondary"></i>
                                        </div>
                                        <div class="text-center">
                                            <i class="bi bi-geo-alt-fill text-success d-block mb-1"></i>
                                            <span class="fw-bold d-block">${train.destination.code}</span>
                                            <span style="font-size: 0.75rem;">${train.destination.name}</span>
                                        </div>
                                    </div>
                                    
                                    <div class="d-grid gap-2">
                                        <a href="/trains/${train.number}/" class="btn btn-outline-primary btn-sm">View Schedule & Route</a>
                                        <a href="/trains/${train.number}/track/" class="btn btn-warning btn-sm fw-bold">Live Track</a>
                                    </div>
                                </div>
                            </div>
                        `;
                        resultsContainer.appendChild(card);
                    });
                })
                .catch(error => {
                    console.error('Error fetching trains:', error);
                    document.getElementById('loadingIndicator').classList.add('d-none');
                    document.getElementById('searchResults').classList.remove('d-none');
                    resultsContainer.innerHTML = `<div class="alert alert-danger w-100">Failed to fetch train data. Please try again.</div>`;
                });
        });
    }
});
