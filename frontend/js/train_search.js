document.addEventListener('DOMContentLoaded', () => {
    const sourceInput = document.getElementById('sourceInput');
    const destInput = document.getElementById('destInput');
    const sourceAutocomplete = document.getElementById('sourceAutocomplete');
    const destAutocomplete = document.getElementById('destAutocomplete');
    const sourceCode = document.getElementById('sourceCode');
    const destCode = document.getElementById('destCode');
    const swapBtn = document.getElementById('swapBtn');
    const searchForm = document.getElementById('searchForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsHeader = document.getElementById('resultsHeader');

    // Default date to today
    document.getElementById('dateInput').valueAsDate = new Date();

    // Autocomplete handler
    let debounceTimer;
    const handleAutocomplete = (input, listContainer, codeField) => {
        input.addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            const val = e.target.value;
            
            if (val.length < 2) {
                listContainer.style.display = 'none';
                return;
            }
            
            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/api/stations/autocomplete/?q=${encodeURIComponent(val)}`);
                    if (res.ok) {
                        const data = await res.json();
                        listContainer.innerHTML = '';
                        if (data.length > 0) {
                            data.forEach(st => {
                                const div = document.createElement('div');
                                div.className = 'autocomplete-item';
                                div.innerHTML = `<strong>${st.name}</strong> <span class="text-muted">(${st.code})</span>`;
                                div.addEventListener('click', () => {
                                    input.value = `${st.name} (${st.code})`;
                                    codeField.value = st.code;
                                    listContainer.style.display = 'none';
                                });
                                listContainer.appendChild(div);
                            });
                            listContainer.style.display = 'block';
                        } else {
                            listContainer.style.display = 'none';
                        }
                    }
                } catch (err) {
                    console.error("Autocomplete error:", err);
                }
            }, 300);
        });
        
        // Hide list when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target !== input && e.target !== listContainer) {
                listContainer.style.display = 'none';
            }
        });
    };

    handleAutocomplete(sourceInput, sourceAutocomplete, sourceCode);
    handleAutocomplete(destInput, destAutocomplete, destCode);

    // Swap button
    swapBtn.addEventListener('click', () => {
        const tempVal = sourceInput.value;
        const tempCode = sourceCode.value;
        
        sourceInput.value = destInput.value;
        sourceCode.value = destCode.value;
        
        destInput.value = tempVal;
        destCode.value = tempCode;
    });

    // Handle form submit
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const src = sourceCode.value || sourceInput.value.split('(').pop().replace(')','').trim();
        const dst = destCode.value || destInput.value.split('(').pop().replace(')','').trim();
        const date = document.getElementById('dateInput').value;
        
        if (!src || !dst) return;
        
        resultsContainer.innerHTML = '';
        resultsHeader.classList.add('d-none');
        loadingIndicator.classList.remove('d-none');
        
        try {
            const response = await fetch(`/api/trains/search/?source=${src}&destination=${dst}&date=${date}`);
            const data = await response.json();
            
            loadingIndicator.classList.add('d-none');
            
            if (response.ok) {
                document.getElementById('resultCount').textContent = data.length;
                document.getElementById('resSource').textContent = sourceInput.value;
                document.getElementById('resDest').textContent = destInput.value;
                resultsHeader.classList.remove('d-none');
                
                if (data.length === 0) {
                    resultsContainer.innerHTML = `
                        <div class="alert alert-warning text-center p-4">
                            <i class="bi bi-info-circle fs-2 d-block mb-2"></i>
                            No direct trains found between these stations.
                        </div>`;
                } else {
                    data.forEach(train => {
                        const typeClass = `type-${train.train_type || 'EXPRESS'}`;
                        const card = document.createElement('a');
                        card.href = `details.html?train=${train.number}&source=${train.source_code}&dest=${train.destination_code}`;
                        card.className = 'train-card bg-white';
                        card.innerHTML = `
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <div>
                                    <h5 class="fw-bold mb-1">${train.number} - ${train.name}</h5>
                                    <span class="type-badge ${typeClass}">${train.train_type || 'EXPRESS'}</span>
                                </div>
                                <div class="text-end">
                                    <span class="duration-badge"><i class="bi bi-clock me-1"></i>${train.duration || '--'}</span>
                                </div>
                            </div>
                            
                            <div class="row text-center align-items-center">
                                <div class="col-4">
                                    <div class="time-display">${train.departure_time ? train.departure_time.substring(0,5) : '--:--'}</div>
                                    <div class="station-display">${train.source}</div>
                                </div>
                                <div class="col-4 position-relative">
                                    <div style="border-top: 2px dashed #ccc; width: 100%; position: absolute; top: 50%;"></div>
                                    <i class="bi bi-train-lightrail fs-4 text-primary bg-white px-2 position-relative"></i>
                                </div>
                                <div class="col-4">
                                    <div class="time-display">${train.arrival_time ? train.arrival_time.substring(0,5) : '--:--'}</div>
                                    <div class="station-display">${train.destination}</div>
                                </div>
                            </div>
                        `;
                        resultsContainer.appendChild(card);
                    });
                }
            } else {
                throw new Error(data.error || 'Failed to search trains');
            }
        } catch (err) {
            loadingIndicator.classList.add('d-none');
            resultsContainer.innerHTML = `<div class="alert alert-danger">Error: ${err.message}</div>`;
        }
    });
});
