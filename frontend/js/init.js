// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();
    
    // Initialize full app (includes event listeners)
    if (typeof initializeApp === 'function') {
        initializeApp();
    }
    
    // Initialize auth observer
    auth.onAuthStateChanged(function(user) {
        currentUser = user;
        updateAuthButton();
        
        // Handle URL routing after auth state change
        if (typeof handleUrlRouting === 'function') {
            setTimeout(handleUrlRouting, 50);
        }
    });
    
    // Show initial page
    showPage('landingPage');
});