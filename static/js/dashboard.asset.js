console.log('dashboard.asset.js loaded');
// Asset tree and asset details logic
function initializeAssetTree() {
    const treeDiv = document.getElementById('asset-tree');
    if (treeDiv) treeDiv.innerHTML = '<div class="text-muted">Loading asset hierarchy...</div>';
    // Robust check for jQuery and jsTree
    if (typeof $ === 'undefined' || typeof $.fn.jstree === 'undefined') {
        console.error('jQuery or jsTree is not loaded.');
        if (treeDiv) treeDiv.innerHTML = '<div class="text-danger">Asset tree cannot load: jQuery or jsTree is missing. Please contact support.</div>';
        return;
    }
    fetch('/api/asset-tree')
        .then(response => response.json())
        .then(data => {
            try {
                $('#asset-tree').jstree('destroy');
            } catch (e) {
                // ignore if not initialized
            }
            $('#asset-tree').jstree({
                core: { 
                    data: data,
                    themes: {
                        name: 'default',
                        responsive: true
                    },
                    multiple: false,
                    animation: 200
                },
                plugins: ['wholerow', 'themes'],
                wholerow: {
                    hover: true
                }
            }).on('ready.jstree', function() {
                // Don't set up click handler immediately - wait for showAssetPanel to be available
                waitForShowAssetPanel();
            });
        })
        .catch((err) => {
            console.error('Asset tree fetch error:', err);
            if (treeDiv) treeDiv.innerHTML = '<div class="text-danger">Failed to load asset hierarchy.</div>';
        });
}

// Function to wait for showAssetPanel to be available
function waitForShowAssetPanel() {
    if (typeof window.showAssetPanel === 'function') {
        setupAssetTreeClickHandler();
    } else {
        setTimeout(waitForShowAssetPanel, 100);
    }
}

function setupAssetTreeClickHandler() {
    // Remove any existing handlers first
    $(document).off('select_node.jstree', '#asset-tree');
    
    // Set up the new handler with more specific targeting
    $('#asset-tree').on('select_node.jstree', function(e, data) {
    const nodeType = data.node.original.type;
    const assetId = nodeType === 'machine' ? data.node.original.machine_id : data.node.original.part_id;
        
    if (nodeType && assetId) {
            // Use the same pattern as the working alert click handler
            window.showAssetPanel('details');
            
            // Load the asset details after ensuring the panel is shown
            setTimeout(() => {
                if (typeof window.loadAssetDetailsInPanel === 'function') {
                    window.loadAssetDetailsInPanel(nodeType, assetId);
                }
            }, 100);
        }
    });
}

function loadAssetDetailsInPanel(assetType, assetId) {
    const container = document.getElementById('asset-details-panel-content');
    if (!container) {
        return;
    }
    
    container.innerHTML = '<div class="text-muted">Loading asset details...</div>';
    
    fetch(`/api/asset/${assetType}/${assetId}`)
        .then(response => response.json())
        .then(data => {
            if (data && !data.error) {
                    // Show asset hierarchy path above details
                    let pathHtml = '';
                    if (data.hierarchy_path) {
                        pathHtml = `<div class='text-secondary mb-2' style='font-size:0.95em;'><i class='fas fa-sitemap'></i> ${data.hierarchy_path}</div>`;
                    }
                
                // Handle different possible name fields
                const assetName = data.name || data.machine_name || data.part_name || 'Unknown Asset';
                const status = data.status || 'Unknown';
                const description = data.description || 'No description available';
                
                // Status badge with color coding
                const statusColors = {
                    'operational': 'success',
                    'critical': 'danger',
                    'warning': 'warning',
                    'maintenance': 'info',
                    'error': 'danger',
                    'in_transit': 'secondary'
                };
                const statusColor = statusColors[status] || 'secondary';
                
                // Device health indicator
                const healthScore = calculateHealthScore(data);
                const healthColor = healthScore >= 80 ? 'success' : healthScore >= 60 ? 'warning' : 'danger';
                
                // Generate charts HTML if chart data exists
                let chartsHtml = '';
                if (data.chart_data) {
                    chartsHtml = generateChartsHtml(data.chart_data, assetName);
                }
                
                // AI recommendations section
                let aiRecommendationsHtml = '';
                if (data.ai_recommendation) {
                    // Clean up the AI response by removing empty lines and formatting properly
                    const cleanedRecommendations = data.ai_recommendation
                        .split('\n')
                        .map(line => line.trim())
                        .filter(line => {
                            // Only keep lines with actual content
                            return line && 
                                   !line.match(/^\s*$/) && // Not just whitespace
                                   line !== '-' && 
                                   line !== '•' && 
                                   line.length > 1 &&
                                   !line.match(/^[-\s]*$/); // Not just dashes and spaces
                        })
                        .map(line => `<p class="mb-2">${line}</p>`)
                        .join('');
                    
                    aiRecommendationsHtml = `
                        <div class="card mb-2">
                            <div class="card-header bg-primary text-white">
                                <i class="fas fa-robot"></i> AI Recommendations
                            </div>
                            <div class="card-body">
                                <div class="ai-recommendation-content">
                                    ${cleanedRecommendations}
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    aiRecommendationsHtml = `
                        <div class="card mb-2">
                            <div class="card-header bg-primary text-white">
                                <i class="fas fa-robot"></i> AI Recommendations
                            </div>
                            <div class="card-body">
                                <div class="text-center text-muted">
                                    <i class="fas fa-spinner fa-spin"></i> Generating AI recommendations...
                                </div>
                            </div>
                        </div>
                    `;
                }
                
                // Alerts section
                let alertsHtml = '';
                if (data.alerts && data.alerts.length > 0) {
                    alertsHtml = `
                        <div class="card mb-2">
                            <div class="card-header bg-warning text-dark">
                                <i class="fas fa-exclamation-triangle"></i> Recent Alerts (${data.alerts.length})
                            </div>
                            <div class="card-body">
                                ${data.alerts.map(alert => `
                                    <div class="alert alert-${alert.severity === 'high' ? 'danger' : alert.severity === 'medium' ? 'warning' : 'info'} mb-2">
                                        <strong>${alert.type}:</strong> ${alert.message}
                                        <br><small class="text-muted">${alert.timestamp}</small>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
                }
                
                // Organ name display (if present)
                let organHtml = '';
                if (data.organ) {
                    organHtml = `<div class='organ-name' style='background:#dc3545;display:inline-block;padding:2px 8px;border-radius:6px;margin-bottom:4px;font-size:0.8rem;'>Organ: ${data.organ}</div>`;
                }
                
                container.innerHTML = `${pathHtml}${organHtml}<h4>${assetName}</h4><p>Status: <span class='badge badge-${status === 'operational' ? 'success' : 'danger'}'>${status}</span></p><p style='margin-bottom:4px;'>${description}</p>${aiRecommendationsHtml}${alertsHtml}${chartsHtml}`;
                
                // Initialize charts after content is loaded
                if (data.chart_data) {
                    initializeCharts(data.chart_data);
                }
                
                // Clean up any remaining empty elements in AI recommendations
                setTimeout(() => {
                    const aiContent = document.querySelector('.ai-recommendation-content');
                    if (aiContent) {
                        const paragraphs = aiContent.querySelectorAll('p');
                        paragraphs.forEach(p => {
                            const text = p.textContent.trim();
                            if (!text || text.length <= 1 || text === '-' || text === '•') {
                                p.remove();
                            }
                        });
                    }
                }, 100);
                
                // Set up minimize functionality
                setupMinimizeFunctionality();
            } else {
                container.innerHTML = `<div class="text-danger">Error: ${data.error || 'No details found for this asset.'}</div>`;
            }
        })
        .catch((err) => {
            container.innerHTML = '<div class="text-danger">Error loading asset details. Please try again.</div>';
        });
}

// Calculate device health score based on various factors
function calculateHealthScore(data) {
    let score = 100;
    
    // Reduce score based on status
    const statusPenalty = {
        'critical': 40,
        'error': 30,
        'warning': 20,
        'maintenance': 15,
        'in_transit': 10
    };
    score -= statusPenalty[data.status] || 0;
    
    // Reduce score based on alerts
    if (data.alerts && data.alerts.length > 0) {
        score -= data.alerts.length * 5;
    }
    
    // Reduce score based on anomalies in chart data
    if (data.chart_data) {
        Object.values(data.chart_data).forEach(metric => {
            if (metric.anomalies) {
                const anomalyCount = metric.anomalies.filter(a => a).length;
                score -= anomalyCount * 2;
            }
        });
    }
    
    return Math.max(0, Math.min(100, score));
}

// Generate charts HTML
function generateChartsHtml(chartData, assetName) {
    const metrics = Object.keys(chartData);
    if (metrics.length === 0) return '';
    
    return `
        <div class="card mb-3">
            <div class="card-header bg-info text-white">
                <i class="fas fa-chart-line"></i> Device Metrics & Health Trends
            </div>
            <div class="card-body">
                <div class="metric-stats">
                    ${metrics.map(metric => `
                        <div class="metric-item">
                            <h6>${metric.replace('_', ' ').toUpperCase()}</h6>
                            ${generateMetricStats(chartData[metric])}
                        </div>
                    `).join('')}
                </div>
                
                <div class="chart-container">
                    <h6 class="chart-title">Sensor Data Trends</h6>
                    ${metrics.map(metric => `
                        <div class="chart-wrapper mb-4">
                            <h6 class="text-capitalize mb-3">${metric.replace('_', ' ')}</h6>
                            <canvas id="chart-${metric}" width="800" height="400"></canvas>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

// Generate metric statistics with new layout
function generateMetricStats(data) {
    if (!data.values || data.values.length === 0) return '<span class="text-muted">No data available</span>';
    
    const values = data.values;
    const anomalies = data.anomalies || [];
    const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(2);
    const max = Math.max(...values).toFixed(2);
    const min = Math.min(...values).toFixed(2);
    const anomalyCount = anomalies.filter(a => a).length;
    
    return `
        <div class="metric-grid">
            <div class="metric-value">
                <div class="metric-label">Avg</div>
                <strong>${avg}</strong>
            </div>
            <div class="metric-value">
                <div class="metric-label">Max</div>
                <strong>${max}</strong>
            </div>
            <div class="metric-value">
                <div class="metric-label">Min</div>
                <strong>${min}</strong>
            </div>
            <div class="metric-value">
                <div class="metric-label">Anomalies</div>
                <strong class="${anomalyCount > 0 ? 'text-danger' : 'text-success'}">${anomalyCount}</strong>
            </div>
        </div>
    `;
}

// Initialize charts using Chart.js
function initializeCharts(chartData) {
    Object.entries(chartData).forEach(([metric, data]) => {
        const ctx = document.getElementById(`chart-${metric}`);
        if (!ctx) return;
        
        // Format timestamps for better display
        const labels = data.labels ? data.labels.map(label => {
            if (typeof label === 'string') {
                try {
                    const date = new Date(label);
                    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                } catch (e) {
                    return label;
                }
            }
            return label;
        }) : [];
        
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: metric.replace('_', ' ').toUpperCase(),
                    data: data.values || [],
                    borderColor: getMetricColor(metric),
                    backgroundColor: getMetricColor(metric, 0.1),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            font: {
                                size: 10
                            }
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        },
                        ticks: {
                            maxTicksLimit: 6,
                            font: {
                                size: 9
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: getMetricColor(metric),
                        borderWidth: 1
                    }
                }
            }
        });
    });
}

// Get color for different metrics
function getMetricColor(metric, alpha = 1) {
    const colors = {
        'temperature': `rgba(255, 99, 132, ${alpha})`,
        'pressure': `rgba(54, 162, 235, ${alpha})`,
        'humidity': `rgba(255, 206, 86, ${alpha})`,
        'vibration': `rgba(75, 192, 192, ${alpha})`,
        'flow': `rgba(153, 102, 255, ${alpha})`,
        'oxygen': `rgba(255, 159, 64, ${alpha})`,
        'ph': `rgba(199, 199, 199, ${alpha})`,
        'altitude': `rgba(83, 102, 255, ${alpha})`
    };
    return colors[metric] || `rgba(128, 128, 128, ${alpha})`;
}

// Setup minimize functionality
function setupMinimizeFunctionality() {
    const minimizeBtn = document.getElementById('minimize-asset-details');
    const assetPanel = document.getElementById('asset-panel');
    
    if (minimizeBtn && assetPanel) {
        minimizeBtn.addEventListener('click', function() {
            if (assetPanel.style.display === 'none') {
                assetPanel.style.display = 'block';
                minimizeBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
            } else {
                assetPanel.style.display = 'none';
                minimizeBtn.innerHTML = '<i class="fas fa-chevron-up"></i>';
            }
        });
    }
}

window.initializeAssetTree = initializeAssetTree;
window.loadAssetDetailsInPanel = loadAssetDetailsInPanel;
window._assetScriptLoaded = true;
