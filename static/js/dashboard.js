// Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabs = document.querySelectorAll('.nav-tabs a');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.parentElement.classList.remove('active'));
            tabContents.forEach(content => content.style.display = 'none');
            
            // Add active class to clicked tab
            this.parentElement.classList.add('active');
            
            // Show corresponding content
            const targetId = this.getAttribute('href').substring(1);
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.style.display = 'block';
            }
        });
    });
    
    // Initialize with first tab active
    if (tabs.length > 0) {
        tabs[0].click();
    }
    
    // Modal functionality
    const modals = document.querySelectorAll('.modal');
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const closeButtons = document.querySelectorAll('.close, .modal-close');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const modalId = this.getAttribute('data-modal');
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.style.display = 'block';
            }
        });
    });
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Close modal when clicking outside
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
    
    // Export functionality
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const format = this.getAttribute('data-format');
            const type = this.getAttribute('data-type');
            
            if (format && type) {
                exportData(type, format);
            }
        });
    });
    
    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableId = this.getAttribute('data-table');
            const table = document.getElementById(tableId);
            
            if (table) {
                filterTable(table, searchTerm);
            }
        });
    });
    
    // Refresh data functionality
    const refreshButtons = document.querySelectorAll('.refresh-btn');
    refreshButtons.forEach(button => {
        button.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            refreshSection(section);
        });
    });
    
    // Auto-refresh stats every 30 seconds
    setInterval(() => {
        refreshStats();
    }, 30000);
    
    // Load initial data
    loadSettings();
    loadSystemInfo();
    
    // Add event listeners
    document.getElementById('dashboard-settings-form').addEventListener('submit', saveDashboardSettings);
    document.getElementById('export-settings-form').addEventListener('submit', saveExportSettings);
    
    // Date range change
    document.getElementById('date-range').addEventListener('change', loadAnalytics);
    
    // Load analytics when analytics section is shown
    const analyticsTab = document.querySelector('button[onclick="showSection(\'analytics\')"]');
    if (analyticsTab) {
        analyticsTab.addEventListener('click', () => {
            setTimeout(loadAnalytics, 100);
        });
    }
});

// Export data function
function exportData(type, format) {
    let url;
    
    if (type === 'kyc') {
        url = `/api/kyc/export/${format}/`;
    } else if (type === 'payments') {
        url = `/api/payments/export/${format}/`;
    } else {
        showNotification('Invalid export type', 'error');
        return;
    }
    
    // Show loading state
    const button = event.target;
    const originalText = button.textContent;
    button.innerHTML = '<span class="spinner"></span> Exporting...';
    button.disabled = true;
    
    fetch(url)
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('Export failed');
        })
        .then(blob => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}_${format}_${new Date().toISOString().split('T')[0]}.${format}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showNotification('Export completed successfully!', 'success');
        })
        .catch(error => {
            console.error('Export error:', error);
            showNotification('Export failed. Please try again.', 'error');
        })
        .finally(() => {
            // Restore button state
            button.textContent = originalText;
            button.disabled = false;
        });
}

// Filter table function
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Refresh section function
function refreshSection(section) {
    const button = event.target;
    const originalText = button.textContent;
    button.innerHTML = '<span class="spinner"></span> Refreshing...';
    button.disabled = true;
    
    // Simulate refresh (replace with actual API call)
    setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
        showNotification('Data refreshed successfully!', 'success');
    }, 1000);
}

// Refresh stats function
function refreshStats() {
    fetch('/api/dashboard/stats/')
        .then(response => response.json())
        .then(data => {
            updateStats(data);
        })
        .catch(error => {
            console.error('Error refreshing stats:', error);
        });
}

// Update stats function
function updateStats(data) {
    Object.keys(data).forEach(key => {
        const element = document.getElementById(`stat-${key}`);
        if (element) {
            element.textContent = data[key];
        }
    });
}

// Show notification function
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    if (type === 'success') {
        notification.style.background = 'var(--success-color)';
    } else if (type === 'error') {
        notification.style.background = 'var(--danger-color)';
    } else {
        notification.style.background = 'var(--primary-color)';
    }
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-GH', {
        style: 'currency',
        currency: 'GHS'
    }).format(amount);
}

// Utility function to format date
function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-GH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Utility function to truncate text
function truncateText(text, maxLength = 50) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Chart.js instances
let paymentTrendsChart = null;
let kycTrendsChart = null;
let paymentStatusChart = null;
let kycStatusChart = null;

// Analytics Functions
function loadAnalytics() {
    const days = document.getElementById('date-range').value;
    
    fetch(`/dashboard/api/analytics/?days=${days}`)
        .then(response => response.json())
        .then(data => {
            createPaymentTrendsChart(data.payments_timeline);
            createKYCTrendsChart(data.kyc_timeline);
            createPaymentStatusChart(data.payment_status_distribution);
            createKYCStatusChart(data.kyc_status_distribution);
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
            showMessage('Error loading analytics data', 'error');
        });
}

function createPaymentTrendsChart(data) {
    const ctx = document.getElementById('paymentTrendsChart').getContext('2d');
    
    if (paymentTrendsChart) {
        paymentTrendsChart.destroy();
    }
    
    paymentTrendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.date),
            datasets: [{
                label: 'Payment Count',
                data: data.map(item => item.count),
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4,
                yAxisID: 'y'
            }, {
                label: 'Payment Amount',
                data: data.map(item => item.amount),
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Count'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Amount'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

function createKYCTrendsChart(data) {
    const ctx = document.getElementById('kycTrendsChart').getContext('2d');
    
    if (kycTrendsChart) {
        kycTrendsChart.destroy();
    }
    
    kycTrendsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.date),
            datasets: [{
                label: 'Total Submissions',
                data: data.map(item => item.total),
                backgroundColor: '#6c757d',
                borderColor: '#6c757d',
                borderWidth: 1
            }, {
                label: 'Successful',
                data: data.map(item => item.success),
                backgroundColor: '#28a745',
                borderColor: '#28a745',
                borderWidth: 1
            }, {
                label: 'Failed',
                data: data.map(item => item.failed),
                backgroundColor: '#dc3545',
                borderColor: '#dc3545',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Submissions'
                    }
                }
            }
        }
    });
}

function createPaymentStatusChart(data) {
    const ctx = document.getElementById('paymentStatusChart').getContext('2d');
    
    if (paymentStatusChart) {
        paymentStatusChart.destroy();
    }
    
    paymentStatusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Success', 'Failed', 'Pending'],
            datasets: [{
                data: [data.success, data.failed, data.pending],
                backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createKYCStatusChart(data) {
    const ctx = document.getElementById('kycStatusChart').getContext('2d');
    
    if (kycStatusChart) {
        kycStatusChart.destroy();
    }
    
    kycStatusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Success', 'Failed', 'Pending'],
            datasets: [{
                data: [data.success, data.failed, data.pending],
                backgroundColor: ['#28a745', '#dc3545', '#ffc107'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function refreshAnalytics() {
    loadAnalytics();
    showMessage('Analytics refreshed successfully', 'success');
}

// Settings Functions
function loadSettings() {
    fetch('/dashboard/api/settings/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('refresh-interval').value = data.dashboard_refresh_interval;
            document.getElementById('date-range-default').value = data.date_range_default;
            document.getElementById('theme-select').value = data.theme;
            document.getElementById('notifications-enabled').checked = data.notifications_enabled;
            document.getElementById('export-format').value = data.export_format;
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            showMessage('Error loading settings', 'error');
        });
}

function saveDashboardSettings(event) {
    event.preventDefault();
    
    const settings = {
        dashboard_refresh_interval: parseInt(document.getElementById('refresh-interval').value),
        date_range_default: parseInt(document.getElementById('date-range-default').value),
        theme: document.getElementById('theme-select').value,
        notifications_enabled: document.getElementById('notifications-enabled').checked,
        export_format: document.getElementById('export-format').value
    };
    
    fetch('/dashboard/api/settings/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        showMessage('Settings saved successfully', 'success');
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showMessage('Error saving settings', 'error');
    });
}

function saveExportSettings(event) {
    event.preventDefault();
    
    const settings = {
        export_format: document.getElementById('export-format').value,
        include_timestamps: document.getElementById('include-timestamps').value === 'true'
    };
    
    fetch('/dashboard/api/settings/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(data => {
        showMessage('Export settings saved successfully', 'success');
    })
    .catch(error => {
        console.error('Error saving export settings:', error);
        showMessage('Error saving export settings', 'error');
    });
}

// System Information Functions
function loadSystemInfo() {
    fetch('/dashboard/api/system-info/')
        .then(response => response.json())
        .then(data => {
            document.getElementById('django-version').textContent = data.django_version;
            document.getElementById('python-version').textContent = data.python_version;
            document.getElementById('database-info').textContent = data.database.split('.')[-1];
            document.getElementById('debug-mode').textContent = data.debug_mode ? 'Enabled' : 'Disabled';
            document.getElementById('timezone').textContent = data.timezone;
        })
        .catch(error => {
            console.error('Error loading system info:', error);
            showMessage('Error loading system information', 'error');
        });
}

function refreshSystemInfo() {
    loadSystemInfo();
    showMessage('System information refreshed', 'success');
}

// Utility Functions
function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Add new message
    document.body.appendChild(messageDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 