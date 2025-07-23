// Main application initialization
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();
    
    // Initialize authentication observer
    if (typeof initAuthObserver === 'function') {
        initAuthObserver();
    }
    
    // Show initial page
    showPage('landingPage');
});
