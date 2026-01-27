// Global variables
let currentFilter = 'all';

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    // Status filter
    const statusFilter = document.getElementById('statusFilter');
    if (statusFilter) {
        statusFilter.addEventListener('change', filterVerifications);
    }
}

// Copy URL to clipboard
function copyUrl() {
    const urlInput = document.querySelector('.url-input');
    urlInput.select();
    urlInput.setSelectionRange(0, 99999);
    
    try {
        document.execCommand('copy');
        showNotification('URL copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy URL', 'error');
    }
}

// Update verification status
function updateStatus(verificationId, status) {
    if (!confirm(`Are you sure you want to ${status} this verification?`)) {
        return;
    }
    
    fetch('/guest-verification/update-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            verification_id: verificationId,
            status: status
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            refreshData();
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to update status', 'error');
    });
}

// Filter verifications by status
function filterVerifications() {
    const filter = document.getElementById('statusFilter').value;
    const cards = document.querySelectorAll('.verification-card');
    
    cards.forEach(card => {
        const status = card.getAttribute('data-status');
        if (filter === 'all' || status === filter) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
    
    currentFilter = filter;
}

// Refresh verification data
function refreshData() {
    if (typeof managerId === 'undefined') {
        console.error('Manager ID not defined');
        return;
    }
    
    showNotification('Refreshing data...', 'info');
    
    fetch(`/guest-verification/api/verifications/${managerId}`)
    .then(response => response.json())
    .then(data => {
        updateVerificationsGrid(data.verifications);
        showNotification('Data refreshed successfully!', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to refresh data', 'error');
    });
}

// Update verifications grid with new data
function updateVerificationsGrid(verifications) {
    const grid = document.getElementById('verificationsGrid');
    
    if (verifications.length === 0) {
        grid.innerHTML = `
            <div class="no-data">
                <p>No verification requests yet.</p>
                <p>Share the QR code or URL above with guests to start receiving verifications.</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = verifications.map(verification => `
        <div class="verification-card" data-status="${verification.status}">
            <div class="card-header">
                <h4>${verification.guest_name}</h4>
                <span class="status-badge status-${verification.status}">${verification.status.charAt(0).toUpperCase() + verification.status.slice(1)}</span>
            </div>
            <div class="card-body">
                <p><strong>Phone:</strong> ${verification.phone}</p>
                <p><strong>Address:</strong> ${verification.address}</p>
                <p><strong>KYC:</strong> ${verification.kyc_number}</p>
                <p><strong>Submitted:</strong> ${formatDate(verification.submitted_at)}</p>
                ${verification.identity_file ? `<p><strong>Document:</strong> <a href="/static/${verification.identity_file}" target="_blank">View Document</a></p>` : ''}
            </div>
            <div class="card-actions">
                ${verification.status === 'pending' ? `
                    <button onclick="updateStatus(${verification.id}, 'approved')" class="approve-btn">Approve</button>
                    <button onclick="updateStatus(${verification.id}, 'rejected')" class="reject-btn">Reject</button>
                ` : ''}
            </div>
        </div>
    `).join('');
    
    // Apply current filter
    filterVerifications();
}

// Format date string
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Style the notification
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    // Set background color based on type
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        info: '#17a2b8',
        warning: '#ffc107'
    };
    notification.style.backgroundColor = colors[type] || colors.info;
    
    // Add to document
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
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