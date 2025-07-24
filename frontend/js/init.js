// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Lucide icons
    lucide.createIcons();
    
    // Initialize full app (includes event listeners)
    if (typeof initializeApp === 'function') {
        initializeApp();
    }
    
    // Re-setup event listeners after DOM content is loaded
    setTimeout(() => {
        if (typeof setupEventListeners === 'function') {
            setupEventListeners();
        }
        lucide.createIcons(); // Re-initialize icons after content load
    }, 100);
    
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
    
    // Add navbar scroll effects
    window.addEventListener('scroll', function() {
        const navbar = document.getElementById('navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }
    });
    
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 120; // Account for fixed navbar height
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
});