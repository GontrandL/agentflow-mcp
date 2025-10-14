/**
 * SmartOrchestrator Dashboard - Real-time Metrics
 *
 * Fetches and displays metrics from Flask API every 5 seconds
 */

// Configuration
const API_BASE = '';
const REFRESH_INTERVAL = 5000; // 5 seconds
const MAX_CHART_POINTS = 20;

// Chart instances
let costChart = null;
let providerChart = null;

// Chart colors
const CHART_COLORS = {
    primary: 'rgba(59, 130, 246, 0.8)',
    success: 'rgba(34, 197, 94, 0.8)',
    warning: 'rgba(251, 191, 36, 0.8)',
    danger: 'rgba(239, 68, 68, 0.8)',
    purple: 'rgba(168, 85, 247, 0.8)',
    orange: 'rgba(249, 115, 22, 0.8)',
};

// Provider color mapping
const PROVIDER_COLORS = [
    CHART_COLORS.primary,
    CHART_COLORS.success,
    CHART_COLORS.warning,
    CHART_COLORS.purple,
    CHART_COLORS.orange,
    CHART_COLORS.danger
];

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initializing...');

    // Initialize charts
    initCharts();

    // Start data fetching
    fetchAllData();
    setInterval(fetchAllData, REFRESH_INTERVAL);

    console.log('Dashboard initialized');
});

/**
 * Initialize Chart.js instances
 */
function initCharts() {
    // Cost Over Time Chart
    const costCtx = document.getElementById('costChart').getContext('2d');
    costChart = new Chart(costCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Cost ($)',
                data: [],
                borderColor: CHART_COLORS.primary,
                backgroundColor: CHART_COLORS.primary.replace('0.8', '0.2'),
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => '$' + value.toFixed(6)
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: context => {
                            return 'Cost: $' + context.parsed.y.toFixed(6);
                        }
                    }
                }
            }
        }
    });

    // Provider Pie Chart
    const providerCtx = document.getElementById('providerChart').getContext('2d');
    providerChart = new Chart(providerCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: PROVIDER_COLORS
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right'
                },
                tooltip: {
                    callbacks: {
                        label: context => {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return label + ': $' + value.toFixed(6);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Fetch all dashboard data
 */
async function fetchAllData() {
    try {
        await Promise.all([
            fetchMetrics(),
            fetchCosts(),
            fetchTasks(),
            fetchTimeline()
        ]);
        updateStatus(true);
    } catch (error) {
        console.error('Error fetching data:', error);
        updateStatus(false);
    }
}

/**
 * Fetch overview metrics
 */
async function fetchMetrics() {
    const response = await fetch(`${API_BASE}/api/metrics`);
    const data = await response.json();

    // Update overview cards
    document.getElementById('totalCost').textContent = '$' + data.total_cost.toFixed(6);
    document.getElementById('totalTasks').textContent = data.total_tasks;
    document.getElementById('avgCost').textContent = '$' + data.avg_cost_per_task.toFixed(6);
    document.getElementById('successRate').textContent = data.success_rate.toFixed(1) + '%';

    // Update uptime
    const uptimeMinutes = Math.floor(data.uptime_seconds / 60);
    const uptimeSeconds = Math.floor(data.uptime_seconds % 60);
    document.getElementById('uptime').textContent =
        `${uptimeMinutes}m ${uptimeSeconds}s`;
}

/**
 * Fetch cost breakdown by provider
 */
async function fetchCosts() {
    const response = await fetch(`${API_BASE}/api/costs`);
    const data = await response.json();

    if (data.providers && data.providers.length > 0) {
        const labels = data.providers.map(p => p.name);
        const costs = data.providers.map(p => p.cost);

        // Update provider chart
        providerChart.data.labels = labels;
        providerChart.data.datasets[0].data = costs;
        providerChart.update();
    }
}

/**
 * Fetch recent tasks
 */
async function fetchTasks() {
    const response = await fetch(`${API_BASE}/api/tasks`);
    const data = await response.json();

    const tbody = document.getElementById('tasksBody');

    if (data.tasks && data.tasks.length > 0) {
        tbody.innerHTML = '';

        // Show only last 10 tasks
        const recentTasks = data.tasks.slice(-10).reverse();

        recentTasks.forEach(task => {
            const row = document.createElement('tr');

            // Format timestamp
            const timestamp = new Date(task.timestamp).toLocaleString();

            // Get provider color class
            const providerClass = getProviderClass(task.provider);

            row.innerHTML = `
                <td>${timestamp}</td>
                <td><span class="badge ${providerClass}">${task.provider}</span></td>
                <td>${task.operation}</td>
                <td>${task.input_tokens.toLocaleString()}</td>
                <td>${task.output_tokens.toLocaleString()}</td>
                <td class="cost-cell">$${task.cost.toFixed(6)}</td>
                <td>${task.latency_ms.toFixed(0)}</td>
            `;

            tbody.appendChild(row);
        });
    } else {
        tbody.innerHTML = '<tr><td colspan="7" class="no-data">No tasks yet. Waiting for data...</td></tr>';
    }
}

/**
 * Fetch timeline data for cost chart
 */
async function fetchTimeline() {
    const response = await fetch(`${API_BASE}/api/timeline`);
    const data = await response.json();

    if (data.timeline && data.timeline.length > 0) {
        // Get last N points
        const timeline = data.timeline.slice(-MAX_CHART_POINTS);

        const labels = timeline.map(t => {
            // Format time (HH:MM)
            const time = t.time.split(' ')[1];
            return time;
        });

        const costs = timeline.map(t => t.cost);

        // Update cost chart
        costChart.data.labels = labels;
        costChart.data.datasets[0].data = costs;
        costChart.update();
    }
}

/**
 * Update connection status indicator
 */
function updateStatus(isConnected) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');

    if (isConnected) {
        statusDot.className = 'status-dot status-connected';
        statusText.textContent = 'Connected';
    } else {
        statusDot.className = 'status-dot status-disconnected';
        statusText.textContent = 'Disconnected';
    }

    // Update last update timestamp
    const now = new Date().toLocaleTimeString();
    document.getElementById('lastUpdate').textContent = now;
}

/**
 * Get CSS class for provider badge
 */
function getProviderClass(provider) {
    const lowerProvider = provider.toLowerCase();

    if (lowerProvider.includes('anthropic') || lowerProvider.includes('claude')) {
        return 'badge-primary';
    } else if (lowerProvider.includes('deepseek')) {
        return 'badge-success';
    } else if (lowerProvider.includes('grok')) {
        return 'badge-warning';
    } else if (lowerProvider.includes('gpt')) {
        return 'badge-purple';
    } else {
        return 'badge-default';
    }
}

/**
 * Format currency
 */
function formatCurrency(value) {
    return '$' + value.toFixed(6);
}

/**
 * Format large numbers
 */
function formatNumber(value) {
    if (value >= 1000000) {
        return (value / 1000000).toFixed(1) + 'M';
    } else if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'K';
    }
    return value.toString();
}
