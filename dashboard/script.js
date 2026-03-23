// AI Employee Dashboard - JavaScript

const API_BASE = 'http://localhost:8000/api';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadActivity();
    loadCharts();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadStats();
        loadActivity();
        loadCharts();
    }, 30000);
});

// Load statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('revenue').textContent = `Rs. ${data.stats.revenue}`;
            document.getElementById('processed').textContent = data.stats.processed;
            document.getElementById('pending').textContent = data.stats.pending;
            document.getElementById('completed').textContent = data.stats.completed;
            document.getElementById('last-updated').textContent = new Date(data.last_updated).toLocaleString();
        }
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Load activity feed
async function loadActivity() {
    try {
        const response = await fetch(`${API_BASE}/activity?limit=10`);
        const data = await response.json();
        
        const feed = document.getElementById('activity-feed');
        
        if (data.success && data.activity.length > 0) {
            feed.innerHTML = data.activity.map(item => `
                <div class="activity-item">
                    <div class="activity-icon ${item.type}">
                        ${item.type === 'completed' ? '✅' : '⏳'}
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${item.file}</div>
                        <div class="activity-time">${new Date(item.timestamp).toLocaleString()}</div>
                    </div>
                </div>
            `).join('');
        } else {
            feed.innerHTML = '<div class="activity-item">No recent activity</div>';
        }
    } catch (error) {
        console.error('Failed to load activity:', error);
        document.getElementById('activity-feed').innerHTML = '<div class="activity-item">Failed to load activity</div>';
    }
}

// Load charts
async function loadCharts() {
    try {
        const response = await fetch(`${API_BASE}/charts`);
        const data = await response.json();
        
        if (data.success) {
            createActivityChart(data.dates, data.completed, data.pending);
            createDistributionChart(data);
        }
    } catch (error) {
        console.error('Failed to load charts:', error);
    }
}

// Create activity trend chart
function createActivityChart(labels, completed, pending) {
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    // Destroy existing chart if exists
    if (window.activityChart) {
        window.activityChart.destroy();
    }
    
    window.activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Completed',
                    data: completed,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Pending',
                    data: pending,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#a1a1aa'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#a1a1aa'
                    }
                }
            }
        }
    });
}

// Create distribution chart
function createDistributionChart(data) {
    const ctx = document.getElementById('distributionChart').getContext('2d');
    
    // Destroy existing chart if exists
    if (window.distributionChart) {
        window.distributionChart.destroy();
    }
    
    const totalCompleted = data.completed.reduce((a, b) => a + b, 0);
    const totalPending = data.pending.reduce((a, b) => a + b, 0);
    
    window.distributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Pending'],
            datasets: [{
                data: [totalCompleted, totalPending],
                backgroundColor: [
                    '#10b981',
                    '#f59e0b'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 0.5)',
                    'rgba(245, 158, 11, 0.5)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                }
            }
        }
    });
}

// Health check
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        const statusText = document.getElementById('status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (data.status === 'healthy') {
            statusText.textContent = 'Online';
            statusDot.style.background = '#10b981';
        } else {
            statusText.textContent = 'Offline';
            statusDot.style.background = '#ef4444';
        }
    } catch (error) {
        const statusText = document.getElementById('status-text');
        const statusDot = document.querySelector('.status-dot');
        statusText.textContent = 'Offline';
        statusDot.style.background = '#ef4444';
    }
}

// Check health every 10 seconds
setInterval(checkHealth, 10000);
checkHealth();
