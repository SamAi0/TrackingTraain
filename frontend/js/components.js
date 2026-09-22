// components.js

function getBasePath() {
    // Determine how many levels deep we are from the frontend root
    const path = window.location.pathname;
    
    // Check if we are at root or index.html
    if (path.endsWith('/') || path.endsWith('index.html') && !path.includes('/pages/')) {
        return './';
    }
    
    // Check if we are inside pages/ folder
    if (path.includes('/pages/')) {
        // e.g. /pages/booking/book.html -> depth is 2 (pages, booking)
        const parts = path.split('/pages/')[1].split('/');
        const depth = parts.length; // usually 2
        return '../'.repeat(depth);
    }
    
    return '../'; // Default fallback
}

function loadNavbar() {
    const basePath = getBasePath();
    const navHtml = `
    <nav class="navbar navbar-expand-lg navbar-dark bg-railway sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold d-flex align-items-center" href="${basePath}index.html">
                <i class="bi bi-train-front me-2 text-warning fs-3"></i>
                <span class="letter-spacing-1">TrackEase</span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link text-white-50 hover-white px-3" href="${basePath}pages/booking/book.html">Book Tickets</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-white-50 hover-white px-3" href="${basePath}pages/pnr/status.html">PNR Status</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-white-50 hover-white px-3 fw-bold text-white" href="${basePath}pages/tracking/track.html"><i class="bi bi-geo-alt-fill text-warning me-1"></i>Track Train</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-white-50 hover-white px-3 fw-bold text-white" href="${basePath}pages/stations/stations.html">Station Explorer <span class="badge bg-warning text-dark ms-1">New</span></a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-white-50 hover-white px-3 fw-bold text-white" href="${basePath}pages/stats/stats.html">Data Insights <span class="badge bg-warning text-dark ms-1">New</span></a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link text-white-50 hover-white px-3" href="${basePath}pages/about/about.html">About Data</a>
                    </li>
                </ul>
                <div class="d-flex auth-buttons" id="navAuthSection">
                    <!-- Auth injected by JS -->
                </div>
                <div class="d-flex align-items-center">
                    <span id="api-status-dot" class="api-status-dot dot-yellow" title="Checking API status..."></span>
                </div>
            </div>
        </div>
    </nav>
    `;
    
    const container = document.getElementById('navbar-container');
    if(container) {
        container.innerHTML = navHtml;
        setupAuthNav(basePath);
        highlightActiveLink();
    }
}

function highlightActiveLink() {
    const currentPath = window.location.pathname;
    const links = document.querySelectorAll('#navbarNav .nav-link');
    links.forEach(link => {
        if(currentPath.includes(link.getAttribute('href').replace('../', '').replace('./', ''))) {
            link.classList.remove('text-white-50');
            link.classList.add('text-white', 'fw-bold', 'active');
            // Remove the 'New' badge if it's the active page
            const badge = link.querySelector('.badge');
            if(badge) badge.remove();
        }
    });
}

function loadFooter() {
    const basePath = getBasePath();
    const footerHtml = `
    <footer class="bg-railway-dark text-white pt-5 pb-3 mt-auto">
        <div class="container">
            <div class="row gy-4">
                <div class="col-lg-4 col-md-6">
                    <h5 class="fw-bold mb-3 d-flex align-items-center">
                        <i class="bi bi-train-front me-2 text-warning"></i>TrackEase
                    </h5>
                    <p class="text-white-50 small pe-lg-4">Your modern, intelligent companion for Indian Railways. Fast bookings, accurate live tracking, and beautiful data insights.</p>
                </div>
                <div class="col-lg-2 col-md-3 col-6">
                    <h6 class="fw-bold mb-3 text-uppercase letter-spacing-1">Services</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-2"><a href="${basePath}pages/booking/book.html" class="text-white-50 text-decoration-none hover-white">Book Ticket</a></li>
                        <li class="mb-2"><a href="${basePath}pages/pnr/status.html" class="text-white-50 text-decoration-none hover-white">PNR Status</a></li>
                        <li class="mb-2"><a href="${basePath}pages/tracking/track.html" class="text-white-50 text-decoration-none hover-white">Track Train</a></li>
                    </ul>
                </div>
                <div class="col-lg-2 col-md-3 col-6">
                    <h6 class="fw-bold mb-3 text-uppercase letter-spacing-1">Explore</h6>
                    <ul class="list-unstyled small">
                        <li class="mb-2"><a href="${basePath}pages/stations/stations.html" class="text-white-50 text-decoration-none hover-white">Station Explorer</a></li>
                        <li class="mb-2"><a href="${basePath}pages/stats/stats.html" class="text-white-50 text-decoration-none hover-white">Stats Dashboard</a></li>
                        <li class="mb-2"><a href="${basePath}pages/about/about.html" class="text-white-50 text-decoration-none hover-white">About Data</a></li>
                    </ul>
                </div>
                <div class="col-lg-4 col-md-6">
                    <h6 class="fw-bold mb-3 text-uppercase letter-spacing-1">Disclaimer</h6>
                    <p class="text-white-50 small">TrackEase uses an open dataset of 8990+ stations and 5208+ trains. The data provided on the Station Explorer and Data Insights pages is static and for demonstration purposes.</p>
                </div>
            </div>
            <hr class="border-secondary mt-4 mb-3">
            <div class="text-center text-white-50 small">
                &copy; 2026 TrackEase Railway Explorer. All rights reserved.
            </div>
        </div>
    </footer>
    `;
    const container = document.getElementById('footer-container');
    if(container) {
        container.innerHTML = footerHtml;
    }
}

function setupAuthNav(basePath) {
    const authSection = document.getElementById('navAuthSection');
    if(!authSection) return;
    
    const token = localStorage.getItem('access_token');
    
    if (token) {
        authSection.innerHTML = `
            <a href="${basePath}pages/user/dashboard.html" class="btn btn-outline-light me-2 fw-bold"><i class="bi bi-person-circle me-1"></i> Dashboard</a>
            <button onclick="logoutUser('${basePath}')" class="btn btn-warning fw-bold">Logout</button>
        `;
    } else {
        authSection.innerHTML = `
            <a href="${basePath}pages/auth/login.html" class="btn btn-outline-light me-2 fw-bold px-4">Login</a>
            <a href="${basePath}pages/auth/register.html" class="btn btn-warning fw-bold px-4">Sign Up</a>
        `;
    }
}

function logoutUser(basePath) {
    logFrontendActivity('User Logout');
    setTimeout(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = basePath + 'index.html';
    }, 200); // Small delay to let the request send
}

function logFrontendActivity(activityType, metadata = {}) {
    const token = localStorage.getItem('access_token');
    
    fetch('http://127.0.0.1:8000/api/tracking/activity/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token ? {'Authorization': 'Bearer ' + token} : {})
        },
        body: JSON.stringify({
            activity_type: activityType,
            ...metadata
        })
    }).catch(e => { /* Ignore errors silently */ });
}

function checkApiStatus() {
    const dot = document.getElementById('api-status-dot');
    if(!dot) return;
    
    const cached = localStorage.getItem('te_api_health');
    const cachedTime = localStorage.getItem('te_api_health_time');
    
    // Use cache if less than 5 minutes old
    if (cached && cachedTime && (Date.now() - parseInt(cachedTime)) < 5 * 60 * 1000) {
        updateApiDot(dot, JSON.parse(cached));
        return;
    }
    
    // Set checking state
    dot.className = 'api-status-dot dot-yellow';
    dot.title = 'API Status: Checking...';
    
    fetch('http://127.0.0.1:8000/api/railway/stations/search/?q=CSMT')
        .then(res => res.json().then(data => ({ status: res.status, ok: res.ok, data })))
        .then(({ status, ok, data }) => {
            let statusObj = {
                source: data.source || 'unknown',
                is_live: data.is_live || (data.source === 'external_api'),
                time: new Date().toLocaleTimeString(),
                fallback: (data.source === 'local_database' || data.source === 'local_mock'),
                error: !ok
            };
            
            localStorage.setItem('te_api_health', JSON.stringify(statusObj));
            localStorage.setItem('te_api_health_time', Date.now().toString());
            updateApiDot(dot, statusObj);
        })
        .catch(err => {
            let statusObj = { source: 'error', is_live: false, fallback: true, error: true, time: new Date().toLocaleTimeString() };
            updateApiDot(dot, statusObj);
        });
}

function updateApiDot(dot, statusObj) {
    let colorClass = 'dot-red';
    let statusText = 'Unavailable / Using Fallback';
    
    if(!statusObj.error && statusObj.is_live && statusObj.source === 'external_api') {
        colorClass = 'dot-green';
        statusText = 'Operational';
    }
    
    dot.className = `api-status-dot ${colorClass}`;
    
    const tooltipText = `API Status: ${statusText}
Data Source: ${statusObj.source.replace('_', ' ')}
Fallback Active: ${statusObj.fallback ? 'Yes' : 'No'}
Last Checked: ${statusObj.time}`;

    dot.title = tooltipText;
}

document.addEventListener('DOMContentLoaded', () => {
    loadNavbar();
    loadFooter();
    checkApiStatus();
});
