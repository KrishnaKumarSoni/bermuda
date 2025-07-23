function updateAuthButton() {
    const authButton = document.getElementById('authButton');
    const authText = document.getElementById('authText');
    const preLoginControls = document.getElementById('preLoginControls');
    const postLoginControls = document.getElementById('postLoginControls');
    const preLoginNav = document.getElementById('preLoginNav');
    const postLoginNav = document.getElementById('postLoginNav');
    
    if (currentUser) {
        // Hide pre-login elements
        if (preLoginControls) preLoginControls.classList.add('hidden');
        if (preLoginNav) preLoginNav.classList.add('hidden');
        
        // Show post-login elements
        if (postLoginControls) postLoginControls.classList.remove('hidden');
        if (postLoginNav) postLoginNav.classList.remove('hidden');
        
        updatePageIndicator();
    } else {
        // Show pre-login elements
        if (preLoginControls) preLoginControls.classList.remove('hidden');
        if (preLoginNav) preLoginNav.classList.remove('hidden');
        
        // Hide post-login elements
        if (postLoginControls) postLoginControls.classList.add('hidden');
        if (postLoginNav) postLoginNav.classList.add('hidden');
        
        // Set default auth button text
        if (authText) authText.textContent = 'Sign In';
        if (authButton) authButton.onclick = signInWithGoogle;
    }
}

function updatePageIndicator() {
    const currentPageElement = document.getElementById('currentPage');
    if (!currentPageElement) return;
    
    const path = window.location.pathname;
    let pageName = 'Dashboard';
    
    if (path.startsWith('/form/')) {
        pageName = 'Form';
    } else if (path === '/create') {
        pageName = 'Create Form';
    } else if (path === '/dashboard') {
        pageName = 'Dashboard';
    }
    
    currentPageElement.textContent = pageName;
}

function signInWithGoogle() {
    const provider = new firebase.auth.GoogleAuthProvider();
    auth.signInWithPopup(provider).catch((error) => {
        showToast('Sign in failed: ' + error.message, 'error');
    });
}

function setupAuthentication() {
    auth.onAuthStateChanged((user) => {
        console.log('🔐 Auth state changed:', user ? 'Signed in' : 'Signed out');
        currentUser = user;
        updateAuthButton();
        
        // Handle routing based on auth state and current URL
        setTimeout(() => {
            handleUrlRouting();
        }, 50);
    });
}