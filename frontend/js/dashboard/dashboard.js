// Navigation functions
function showPage(pageId) {
    console.log(`🔄 Switching to page: ${pageId}`);
    
    const pages = ['landingPage', 'dashboardPage', 'createFormPage', 'chatPage'];
    pages.forEach(page => {
        const element = document.getElementById(page);
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
            console.log(`✅ Hidden page: ${page}`);
        }
    });
    
    // Also hide nested form elements to prevent bleed-through
    const nestedElements = ['formCreationStep', 'formBuilder'];
    nestedElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
            console.log(`✅ Hidden nested element: ${elementId}`);
        }
    });
    
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.style.display = 'block';
        targetPage.classList.remove('hidden');
        console.log(`✅ Shown target page: ${pageId}`);
        
        // Show appropriate nested elements for the target page
        if (pageId === 'createFormPage') {
            const formCreationStep = document.getElementById('formCreationStep');
            if (formCreationStep) {
                formCreationStep.style.display = 'block';
                formCreationStep.classList.remove('hidden');
                console.log(`✅ Shown formCreationStep for createFormPage`);
            }
        }
    } else {
        console.error(`❌ Target page not found: ${pageId}`);
    }
    
    // Update URL without reloading page
    let newPath = '/';
    if (pageId === 'dashboardPage') newPath = '/dashboard';
    else if (pageId === 'createFormPage') newPath = '/create';
    else if (pageId === 'chatPage') newPath = window.location.pathname; // Keep existing chat path
    
    if (window.location.pathname !== newPath && pageId !== 'chatPage') {
        window.history.pushState({}, '', newPath);
    }
}

function showPage(pageId) {
    console.log(`🔄 Switching to page: ${pageId}`);
    
    const pages = ['landingPage', 'dashboardPage', 'createFormPage', 'chatPage'];
    pages.forEach(page => {
        const element = document.getElementById(page);
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
            console.log(`✅ Hidden page: ${page}`);
        }
    });
    
    // Also hide nested form elements to prevent bleed-through
    const nestedElements = ['formCreationStep', 'formBuilder'];
    nestedElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
            console.log(`✅ Hidden nested element: ${elementId}`);
        }
    });
    
    const targetPage = document.getElementById(pageId);
    if (targetPage) {
        targetPage.style.display = 'block';
        targetPage.classList.remove('hidden');
        console.log(`✅ Shown target page: ${pageId}`);
        
        // Show appropriate nested elements for the target page
        if (pageId === 'createFormPage') {
            const formCreationStep = document.getElementById('formCreationStep');
            if (formCreationStep) {
                formCreationStep.style.display = 'block';
                formCreationStep.classList.remove('hidden');
                console.log(`✅ Shown formCreationStep for createFormPage`);
            }
        }
    } else {
        console.error(`❌ Target page not found: ${pageId}`);
    }
    
    // Update URL without reloading page
    let newPath = '/';
    if (pageId === 'dashboardPage') newPath = '/dashboard';
    else if (pageId === 'createFormPage') newPath = '/create';
    else if (pageId === 'chatPage') newPath = window.location.pathname; // Keep existing chat path
    
    if (window.location.pathname !== newPath && pageId !== 'chatPage') {
        window.history.pushState({}, '', newPath);
    }
}

function showDashboard() {
    showPage('dashboardPage');
    loadUserForms();
    // Clear any form builder state
    resetFormBuilder();
}