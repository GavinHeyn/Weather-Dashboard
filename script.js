// Additional JavaScript can go here

// Auto-refresh notification
setTimeout(() => {
    const notification = document.createElement('div');
    notification.className = 'alert alert-info alert-dismissible fade show position-fixed bottom-0 end-0 m-3';
    notification.style.zIndex = '1050';
    notification.innerHTML = `
        <strong>Weather Update Available</strong>
        <p class="mb-0">Data was last updated 10 minutes ago. Refresh for latest.</p>
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <button type="button" class="btn btn-sm btn-primary ms-2" onclick="location.reload()">
            Refresh Now
        </button>
    `;
    document.body.appendChild(notification);
}, 600000); // 10 minutes

// Add loading animation for form submissions
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Loading...';
                submitBtn.disabled = true;
            }
        });
    });
});