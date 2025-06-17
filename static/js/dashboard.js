// DEBUG: Confirm dashboard.js is loaded
console.log('dashboard.js loaded');

// Dashboard JavaScript

// --- Panel Tab Logic ---
function showAssetPanel(tab) {
    const panel = document.getElementById('asset-panel');
    if (!panel) {
        console.error('Asset panel element not found!');
        return;
    }
    panel.style.display = 'block';
    panel.style.width = '420px'; // Frugal width
    panel.style.left = 'calc(50vw - 210px)';
    const alertsPanel = document.getElementById('alerts-panel');
    if (alertsPanel) alertsPanel.style.display = 'none';
    if (tab === 'tree') {
        $('#assetPanelTabs a#asset-tree-tab').tab('show');
    } else {
        $('#assetPanelTabs a#asset-details-tab').tab('show');
    }
}
function hideAssetPanel() {
    const panel = document.getElementById('asset-panel');
    if (panel) panel.style.display = 'none';
}
function showAlertsPanel() {
    const panel = document.getElementById('alerts-panel');
    if (!panel) {
        console.error('Alerts panel element not found!');
        return;
    }
    panel.style.display = 'block';
    panel.style.width = '420px'; // Frugal width
    panel.style.left = 'calc(50vw - 210px)';
    const assetPanel = document.getElementById('asset-panel');
    if (assetPanel) assetPanel.style.display = 'none';
}

const assetTabBtn = document.getElementById('show-asset-panel-tab');
if (assetTabBtn) assetTabBtn.onclick = function() { showAssetPanel('tree'); };
const alertsTabBtn = document.getElementById('show-alerts-tab');
if (alertsTabBtn) alertsTabBtn.onclick = function() { showAlertsPanel(); };
const minAssetBtn = document.getElementById('minimize-asset-panel');
if (minAssetBtn) minAssetBtn.onclick = function() { hideAssetPanel(); };
const minAlertsBtn = document.getElementById('minimize-alerts');
if (minAlertsBtn) minAlertsBtn.onclick = function() { document.getElementById('alerts-panel').style.display = 'none'; };
const backToTreeBtn = document.getElementById('back-to-asset-tree');
if (backToTreeBtn) backToTreeBtn.onclick = function() { $('#assetPanelTabs a#asset-tree-tab').tab('show'); };

// Add RAG panel logic
const ragTabBtn = document.getElementById('show-rag-panel-tab');
const ragPanel = document.getElementById('rag-panel');
const minRagBtn = document.getElementById('minimize-rag-panel');
if (ragTabBtn) ragTabBtn.onclick = function() { ragPanel.style.display = 'block'; };
if (minRagBtn) minRagBtn.onclick = function() { ragPanel.style.display = 'none'; };

// RAG search form logic
const ragForm = document.getElementById('rag-dashboard-search-form');
const ragInput = document.getElementById('rag-dashboard-search-text');
const ragResults = document.getElementById('rag-dashboard-search-results');
const ragSummary = document.getElementById('rag-dashboard-ai-summary');
if (ragForm) {
    ragForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const searchText = ragInput.value.trim();
        if (searchText) {
            ragResults.innerHTML = `<div class='text-center text-muted'><i class='fas fa-spinner fa-spin'></i> Searching...</div>`;
            ragSummary.innerHTML = `<div class='text-center text-muted'><i class='fas fa-spinner fa-spin'></i> Generating summary...</div>`;
            fetch('/api/rag/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ search_text: searchText })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    ragResults.innerHTML = `<div class='alert alert-danger'><i class='fas fa-exclamation-circle'></i> ${data.error}</div>`;
                    ragSummary.innerHTML = '';
                } else {
                    if (data.results && data.results.length > 0) {
                        const resultsHtml = data.results.map(result => `
                            <div class='result-item'>
                                <h5>${result.title || 'Untitled'}</h5>
                                <p>${result.content}</p>
                                <div class='result-meta'><span class='badge badge-info'>Score: ${(result.score * 100).toFixed(1)}%</span></div>
                            </div>
                        `).join('');
                        ragResults.innerHTML = resultsHtml;
                    } else {
                        ragResults.innerHTML = `<div class='alert alert-info'><i class='fas fa-info-circle'></i> No results found</div>`;
                    }
                    if (data.summary) {
                        ragSummary.innerHTML = `<div class='summary-content'>${data.summary}</div>`;
                    } else {
                        ragSummary.innerHTML = `<div class='alert alert-info'><i class='fas fa-info-circle'></i> No summary available</div>`;
                    }
                }
            })
            .catch(error => {
                ragResults.innerHTML = `<div class='alert alert-danger'><i class='fas fa-exclamation-circle'></i> Search failed</div>`;
                ragSummary.innerHTML = '';
            });
        }
    });
}

// Add Geo Advisor panel logic
const geoAdvisorTabBtn = document.getElementById('show-geo-advisor-tab');
const geoAdvisorPanel = document.getElementById('geo-advisor-panel');
const minGeoAdvisorBtn = document.getElementById('minimize-geo-advisor-panel');
const geoAdvisorBestPractices = document.getElementById('geo-advisor-best-practices');
const geoAdvisorImages = document.getElementById('geo-advisor-images');

// Add input and button for advisor queries
if (geoAdvisorBestPractices && !document.getElementById('geo-advisor-query-form')) {
    const form = document.createElement('form');
    form.id = 'geo-advisor-query-form';
    form.className = 'mb-2';
    form.innerHTML = `
        <div class="form-group mb-2">
            <input type="text" class="form-control" id="geo-advisor-query-text" placeholder="Ask about geospatial data modeling..." autocomplete="off" />
        </div>
        <button type="submit" class="btn btn-success btn-block"><i class="fas fa-search"></i> Advisor Search</button>
    `;
    geoAdvisorBestPractices.prepend(form);
}

function fetchGeoAdvisorResults(query) {
    geoAdvisorBestPractices.innerHTML = `<div class='text-center text-muted'><i class='fas fa-spinner fa-spin'></i> Searching best practices...</div>`;
    fetch('/api/geo-advisor/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ search_text: query })
    })
    .then(response => response.json())
    .then(data => {
        // Remove duplicate results by title/content
        let unique = [];
        let seen = new Set();
        if (data.results && data.results.length > 0) {
            data.results.forEach(result => {
                const key = (result.title || '') + (result.content || '');
                if (!seen.has(key)) {
                    unique.push(result);
                    seen.add(key);
                }
            });
        }
        // Show Gemini summary as advisor message
        let summaryHtml = '';
        if (data.summary) {
            summaryHtml = `
                <div class='advisor-summary-card mb-3'>
                    <div class='advisor-avatar'>🧑‍💼</div>
                    <div class='advisor-message'>
                        <b>Advisor:</b> <span>${data.summary}</span>
                    </div>
                </div>
            `;
        }
        // Show best practices as cards
        let resultsHtml = '';
        if (unique.length > 0) {
            resultsHtml = unique.map(result => `
                <div class='advisor-card mb-2'>
                    <div class='advisor-card-header'>
                        <span class='advisor-title'>${result.title || 'Untitled'}</span>
                        <span class='advisor-score badge badge-info ml-2'>Score: ${(result.score * 100).toFixed(1)}%</span>
                    </div>
                    <div class='advisor-card-content'>${result.content}</div>
                </div>
            `).join('');
        } else {
            resultsHtml = `<div class='alert alert-info'><i class='fas fa-info-circle'></i> No best practices found</div>`;
        }
        geoAdvisorBestPractices.innerHTML = summaryHtml + resultsHtml;
    })
    .catch(() => {
        geoAdvisorBestPractices.innerHTML = `<div class='alert alert-danger'><i class='fas fa-exclamation-circle'></i> Advisor search failed</div>`;
    });
}

if (geoAdvisorTabBtn) geoAdvisorTabBtn.onclick = function() {
    geoAdvisorPanel.style.display = 'block';
    // Default query for first open
    fetchGeoAdvisorResults('geospatial data modeling best practices');
};
if (minGeoAdvisorBtn) minGeoAdvisorBtn.onclick = function() { geoAdvisorPanel.style.display = 'none'; };

// Advisor query form submit
const geoAdvisorQueryForm = document.getElementById('geo-advisor-query-form');
if (geoAdvisorQueryForm) {
    geoAdvisorQueryForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = document.getElementById('geo-advisor-query-text').value.trim();
        if (query) fetchGeoAdvisorResults(query);
    });
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initializing...');
    
    // Initialize metrics
    initializeMetrics();
    
    // Initialize map
    if (typeof initializeMap === 'function') {
        initializeMap();
    }
    
    // Initialize asset panel functionality
    initializeAssetPanel();
    
    // Initialize alerts panel functionality
    initializeAlertsPanel();
    
    // Initialize help modal
    initializeHelpModal();
    
    // Start periodic updates
    startPeriodicUpdates();
});

function initializeMetrics() {
    console.log('Initializing metrics...');
    
    // Check if metrics cards exist
    const metricsCards = document.getElementById('metrics-cards');
    if (!metricsCards) {
        console.error('Metrics cards container not found!');
        return;
    }
    
    console.log('Metrics cards container found, updating metrics...');
    
    // Update metrics with initial values
    updateMetrics();
    
    // Add animation to metrics
    animateMetrics();
}

function updateMetrics() {
    console.log('Fetching metrics from database...');
    
    // Fetch real data from database
    fetch('/api/metrics')
        .then(response => {
            console.log('Metrics API response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Metrics data received:', data);
            
            // Update each metric with real data
            const metrics = {
                'total-organs': data.total_organs || 0,
                'total-flights': data.total_flights || 0,
                'total-devices': data.total_devices || 0,
                'active-failures': data.active_failures || 0,
                'avg-response': data.avg_response || '0.0m',
                'success-rate': data.success_rate || '0.0%',
                // NEW: Medical organ metrics
                'total-available-organs': data.total_available_organs || 0,
                'total-in-transit-organs': data.total_in_transit_organs || 0,
                'total-reserved-organs': data.total_reserved_organs || 0,
                'total-delivered-organs': data.total_delivered_organs || 0
            };
            
            console.log('Processed metrics:', metrics);
            
            // Update each metric with animation
            Object.keys(metrics).forEach(metricId => {
                const element = document.getElementById(metricId);
                if (element) {
                    const currentValue = element.textContent;
                    const newValue = metrics[metricId];
                    
                    console.log(`Updating ${metricId}: ${currentValue} -> ${newValue}`);
                    
                    // Animate the change
                    animateValueChange(element, currentValue, newValue);
                } else {
                    console.error(`Element with id '${metricId}' not found!`);
                }
            });
            
            // Ensure metrics cards are visible and properly sized
            ensureMetricsVisibility();
        })
        .catch(error => {
            console.error('Error fetching metrics:', error);
            // Fallback to simulated data if API fails
            updateMetricsFallback();
        });
}

function ensureMetricsVisibility() {
    const metricsContainer = document.getElementById('metrics-cards');
    if (metricsContainer) {
        // Ensure container is visible and properly positioned
        metricsContainer.style.display = 'flex';
        metricsContainer.style.visibility = 'visible';
        metricsContainer.style.opacity = '1';
        
        // Force layout recalculation
        metricsContainer.offsetHeight;
        
        // Ensure all metric cards are visible
        const metricCards = metricsContainer.querySelectorAll('.metric-card');
        metricCards.forEach(card => {
            card.style.display = 'flex';
            card.style.flexDirection = 'column';
            card.style.visibility = 'visible';
            card.style.opacity = '1';
        });
    }
}

function updateMetricsFallback() {
    // Fallback simulated data if API fails
    const metrics = {
        'total-organs': Math.floor(Math.random() * 500) + 1200,
        'total-flights': Math.floor(Math.random() * 200) + 800,
        'total-devices': Math.floor(Math.random() * 1000) + 3000,
        'active-failures': Math.floor(Math.random() * 10) + 15,
        'avg-response': (Math.random() * 2 + 1.5).toFixed(1) + 'm',
        'success-rate': (Math.random() * 0.5 + 99.5).toFixed(1) + '%'
    };
    
    // Update each metric with animation
    Object.keys(metrics).forEach(metricId => {
        const element = document.getElementById(metricId);
        if (element) {
            const currentValue = element.textContent;
            const newValue = metrics[metricId];
            
            // Animate the change
            animateValueChange(element, currentValue, newValue);
        }
    });
}

function animateValueChange(element, oldValue, newValue) {
    // Remove any existing animation
    element.style.transition = 'none';
    
    // Start animation
    element.style.transition = 'all 0.5s ease-in-out';
    element.style.transform = 'scale(1.1)';
    element.style.color = '#c82333';
    
    // Update value
    element.textContent = newValue;
    
    // Reset animation
    setTimeout(() => {
        element.style.transform = 'scale(1)';
        element.style.color = '#dc3545';
    }, 500);
}

function animateMetrics() {
    // Add subtle pulse animation to metric cards
    const metricCards = document.querySelectorAll('#metrics-cards .metric-card');
    
    metricCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('metric-pulse');
        
        // Ensure card content is properly structured
        const icon = card.querySelector('.metric-icon');
        const content = card.querySelector('.metric-content');
        const value = card.querySelector('.metric-value');
        const label = card.querySelector('.metric-label');
        
        if (icon && content && value && label) {
            // Ensure proper display
            icon.style.display = 'flex';
            content.style.display = 'flex';
            content.style.flexDirection = 'column';
            value.style.display = 'block';
            label.style.display = 'block';
        }
    });
}

function startPeriodicUpdates() {
    // Update all metrics every 30 seconds with real data
    setInterval(updateMetrics, 30000);
    
    // Update metrics every 10 seconds for more frequent updates
    setInterval(updateMetrics, 10000);
}

function initializeAssetPanel() {
    console.log('Initializing asset panel...');
    
    // Initialize asset tree
    if (typeof window.initializeAssetTree === 'function') {
        window.initializeAssetTree();
    } else {
        console.error('initializeAssetTree is not defined. Check dashboard.asset.js load order.');
        const treeDiv = document.getElementById('asset-tree');
        if (treeDiv) treeDiv.innerHTML = '<div class="text-danger">Asset tree failed to load. Please contact support.</div>';
    }
    
    // Add click handler for alert items to show asset details
    document.getElementById('recent-alerts-list')?.addEventListener('click', function(e) {
        let target = e.target;
        while (target && !target.classList.contains('alert-item') && target !== this) {
            target = target.parentElement;
        }
        if (target && target.classList.contains('alert-item')) {
            const assetType = target.getAttribute('data-asset-type');
            const assetId = target.getAttribute('data-asset-id');
            if (assetType && assetId) {
                showAssetPanel('details');
                window.loadAssetDetailsInPanel(assetType, assetId);
            }
        }
    });
}

function initializeAlertsPanel() {
    console.log('Initializing alerts panel...');
    // Alerts panel functionality is handled in the HTML and CSS
}

function initializeHelpModal() {
    console.log('Initializing help modal...');
    if (typeof window.setupHelpButton === 'function') {
        window.setupHelpButton();
    }
}

window.showAssetPanel = showAssetPanel;
