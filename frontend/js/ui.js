async function inferFormFromText() {
    const textDump = document.getElementById('textDump').value.trim();
    
    if (!textDump) {
        showToast('Please enter some text to generate a form', 'error');
        return;
    }
    
    if (!currentUser) {
        showToast('Please sign in to create forms', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const token = await currentUser.getIdToken();
        const response = await fetch('https://us-central1-bermuda-01.cloudfunctions.net/api/infer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ dump: textDump })
        });
        
        if (!response.ok) {
            throw new Error('Failed to generate form');
        }
        
        const formData = await response.json();
        currentFormData = formData;
        
        displayFormBuilder(formData);
        showToast('Form generated successfully!', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to generate form. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function getDemographicDescription(name) {
    const descriptions = {
        'Age': 'Age range or specific age',
        'Gender': 'Gender identity',
        'Location': 'Geographic location',
        'Education': 'Educational background',
        'Income': 'Household income range',
        'Occupation': 'Job title or industry',
        'Ethnicity': 'Ethnic background'
    };
    return descriptions[name] || 'Demographic information';
}

function gatherFormData() {
    const formData = {
        questions: [],
        demographics: []
    };
    
    // Gather questions
    const questionElements = document.querySelectorAll('.question-item');
    questionElements.forEach(element => {
        const textInput = element.querySelector('.question-text');
        const typeSelect = element.querySelector('.question-type');
        const enabledToggle = element.querySelector('.question-enabled');
        
        if (textInput && typeSelect) {
            const question = {
                text: textInput.value.trim(),
                type: typeSelect.value,
                enabled: enabledToggle ? enabledToggle.checked : true
            };
            
            // Gather options for multiple choice questions
            if (['multiple_choice', 'yes_no', 'rating'].includes(question.type)) {
                const optionInputs = element.querySelectorAll('.option-input');
                question.options = [];
                optionInputs.forEach(input => {
                    if (input.value.trim()) {
                        question.options.push(input.value.trim());
                    }
                });
            }
            
            if (question.text) {
                formData.questions.push(question);
            }
        }
    });
    
    // Gather demographics
    const demographicElements = document.querySelectorAll('.demographic-item');
    demographicElements.forEach(element => {
        const textInput = element.querySelector('.demographic-text');
        const enabledToggle = element.querySelector('.demographic-enabled');
        
        if (textInput) {
            const demographic = {
                text: textInput.value.trim(),
                enabled: enabledToggle ? enabledToggle.checked : true
            };
            
            if (demographic.text) {
                formData.demographics.push(demographic);
            }
        }
    });
    
    return formData;
}

function clearFormBuilderState() {
    // Clear editing state
    window.currentEditingFormId = null;
    
    // Clear form builder
    const titleInput = document.getElementById('formTitle');
    if (titleInput) titleInput.value = '';
    
    const questionsList = document.getElementById('questionsList');
    if (questionsList) questionsList.innerHTML = '';
    
    const demographicsList = document.getElementById('demographicsList');
    if (demographicsList) demographicsList.innerHTML = '';
    
    // Reset save button text
    const saveButton = document.getElementById('saveFormBtn');
    if (saveButton) {
        saveButton.innerHTML = '<i data-lucide="rocket" class="w-5 h-5 mr-2"></i>Launch Form';
        // Re-initialize icons
        lucide.createIcons();
    }
    
    // Clear current form data
    currentFormData = null;
}

function openForm(formId) {
    // Navigate to the form responses/management view
    showToast('Opening form responses...', 'info');
    // For now, just show the form in a new tab
    window.open(`/form/${formId}`, '_blank');
}

async function viewResponses(formId) {
    if (!currentUser) {
        showToast('Please sign in to view responses', 'error');
        return;
    }

    showLoading();

    try {
        const token = await currentUser.getIdToken();
        const response = await fetch(`https://us-central1-bermuda-01.cloudfunctions.net/api/forms/${formId}/responses`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to load responses');
        }

        const responses = await response.json();

        renderResponsesModal(responses, formId);

    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to load responses', 'error');
    } finally {
        hideLoading();
    }
}

function renderResponsesModal(responses, formId) {
    const modal = document.getElementById('responsesModal');
    const body = document.getElementById('responsesModalBody');
    const title = document.getElementById('responsesModalTitle');

    title.textContent = `Responses (${responses.length})`;
    body.innerHTML = '';

    if (responses.length === 0) {
        body.innerHTML = '<p class="text-gray-600">No responses yet.</p>';
    } else {
        const first = responses[0];
        const qObj = first.questions || {};
        const headers = Object.keys(qObj);

        if (headers.length === 0) {
            // Fallback: show raw JSON
            body.innerHTML = `<pre class="text-xs bg-gray-50 p-4 rounded">${JSON.stringify(responses, null, 2)}</pre>`;
            return;
        }

        const table = document.createElement('table');
        table.className = 'min-w-full border divide-y divide-gray-200 text-sm';

        const thead = document.createElement('thead');
        thead.innerHTML = `<tr>${headers.map(h=>`<th class=\"px-4 py-2 text-left font-semibold text-gray-700\">${h}</th>`).join('')}</tr>`;
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        responses.forEach(resp=>{
            const row = document.createElement('tr');
            row.className = 'odd:bg-gray-50 hover:bg-orange-50';
            row.innerHTML = headers.map(h=>`<td class=\"px-4 py-2\">${(resp.questions||{})[h] ?? ''}</td>`).join('');
            tbody.appendChild(row);
        });
        table.appendChild(tbody);
        body.appendChild(table);
    }

    modal.classList.remove('hidden');

    document.getElementById('closeResponsesModal').onclick = () => {
        modal.classList.add('hidden');
    };

    // Escape key to close
    window.addEventListener('keydown', function escListener(e){
        if(e.key==='Escape'){
            modal.classList.add('hidden');
            window.removeEventListener('keydown', escListener);
        }
    });

    // Re-render lucide icons in modal
    lucide.createIcons();
}

function shareForm(formId) {
    const shareUrl = `${window.location.origin}/form/${formId}`;
    
    // Copy to clipboard
    if (navigator.clipboard) {
        navigator.clipboard.writeText(shareUrl).then(() => {
            showToast('Form link copied to clipboard!', 'success');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = shareUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showToast('Form link copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = shareUrl;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Form link copied to clipboard!', 'success');
    }
}

async function deleteForm(formId) {
    if (!confirm('Are you sure you want to delete this form? This action cannot be undone.')) return;
    
    if (!currentUser) {
        showToast('Please sign in to delete forms', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const token = await currentUser.getIdToken();
        
        // Try DELETE first, fallback to POST workaround if CORS fails
        let response;
        try {
            response = await fetch(`https://us-central1-bermuda-01.cloudfunctions.net/api/forms/${formId}`, {
                method: 'DELETE',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
        } catch (corsError) {
            // CORS workaround: Use POST with _method parameter
            console.log('DELETE blocked by CORS, trying POST workaround...');
            response = await fetch(`https://us-central1-bermuda-01.cloudfunctions.net/api/forms/${formId}`, {
                method: 'POST',
                headers: { 
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ _method: 'DELETE' })
            });
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.error || `HTTP error! status: ${response.status}`;
            throw new Error(errorMessage);
        }
        
        const data = await response.json();
        showToast(data.message || 'Form deleted successfully', 'success');
        loadUserForms();
    } catch (error) {
        console.error('Delete form error:', error);
        showToast(`Failed to delete form: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function editForm(formId) {
    if (!currentUser) {
        showToast('Please sign in to edit forms', 'error');
        return;
    }
    
    showLoading();
    
    try {
        // Fetch the current form data
        const token = await currentUser.getIdToken();
        const response = await fetch(`https://us-central1-bermuda-01.cloudfunctions.net/api/forms/${formId}`, {
            method: 'GET',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`Failed to fetch form data: ${response.status}`);
        }
        
        const formData = await response.json();
        
        // Switch to form creation page and populate with existing data
        showPage('createFormPage');
        
        // Set editing mode
        window.currentEditingFormId = formId;
        
        // Hide form creation step, show form builder
        const formCreationStep = document.getElementById('formCreationStep');
        const formBuilder = document.getElementById('formBuilder');
        if (formCreationStep) {
            formCreationStep.style.display = 'none';
            formCreationStep.classList.add('hidden');
        }
        if (formBuilder) {
            formBuilder.style.display = 'block';
            formBuilder.classList.remove('hidden');
        }
        
        // Store the form data globally
        currentFormData = formData;
        
        // Populate the form builder with existing data
        populateFormBuilder(formData, formId);
        
        showToast('Form loaded for editing', 'success');
        
    } catch (error) {
        console.error('Edit form error:', error);
        showToast(`Failed to load form for editing: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function populateFormBuilder(formData, formId) {
    // Store the form ID for updates
    window.currentEditingFormId = formId;
    
    // Populate title
    const titleInput = document.getElementById('formTitle');
    if (titleInput) {
        titleInput.value = formData.title || '';
    }
    
    // Use the existing render functions
    if (formData.questions) {
        renderQuestions(formData.questions);
        updateQuestionCount();
    }
    
    if (formData.demographics) {
        renderDemographics(formData.demographics);
    }
    
    // Update the save button
    const saveButton = document.getElementById('saveFormBtn');
    if (saveButton) {
        saveButton.innerHTML = '<i data-lucide="save" class="w-5 h-5 mr-2"></i>Update Form';
        // Re-initialize icons
        lucide.createIcons();
    }
}

function showShareModal(formId, shareUrl) {
    document.getElementById('shareUrl').value = shareUrl;
    document.getElementById('shareModal').classList.remove('hidden');
}

function copyShareLink() {
    const shareUrl = document.getElementById('shareUrl');
    shareUrl.select();
    shareUrl.setSelectionRange(0, 99999);
    document.execCommand('copy');
    showToast('Link copied to clipboard!', 'success');
}

function updateMessageCount() {
    document.getElementById('messageCount').textContent = `Messages ${messageCount}`;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatMessages');
    
    // Remove existing typing indicator if present
    const existingIndicator = document.getElementById('typingIndicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'flex justify-start chat-message-enter';
    
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function getDeviceId() {
    let deviceId = localStorage.getItem('deviceId');
    if (!deviceId) {
        deviceId = generateSessionId();
        localStorage.setItem('deviceId', deviceId);
    }
    return deviceId;
}

async function loadUserForms() {
    if (!currentUser) return;
    
    showLoading();
    
    try {
        const token = await currentUser.getIdToken();
        const response = await fetch('https://us-central1-bermuda-01.cloudfunctions.net/api/forms', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load forms');
        }
        
        const forms = await response.json();
        displayForms(forms);
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to load forms', 'error');
    } finally {
        hideLoading();
    }
}

function displayForms(forms) {
    const formsGrid = document.getElementById('formsGrid');
    const emptyState = document.getElementById('emptyState');
    
    if (forms.length === 0) {
        formsGrid.classList.add('hidden');
        emptyState.classList.remove('hidden');
        return;
    }
    
    emptyState.classList.add('hidden');
    formsGrid.classList.remove('hidden');
    
    formsGrid.innerHTML = forms.map(form => `
        <div class="card p-6">
            <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                    <h3 class="font-heading font-bold mb-2" style="font-size: 1.125rem; color: var(--text-primary);">${form.title}</h3>
                    <div class="flex items-center space-x-4 font-body" style="font-size: 0.875rem; color: var(--text-secondary);">
                        <span>Created ${new Date(form.created_at).toLocaleDateString()}</span>
                        <div class="px-2 py-1 rounded-full" style="background-color: var(--primary); color: white; font-size: 0.75rem;">
                            ${form.response_count || 0}
                        </div>
                    </div>
                </div>
                <div class="w-3 h-3 rounded-full" style="background-color: var(--success);"></div>
            </div>
            
            <!-- Action Buttons -->
            <div class="grid grid-cols-2 gap-2 mb-4">
                <button class="btn-secondary py-2 px-3" style="font-size: 0.875rem;" onclick="testChat('${form.form_id}')">
                    <i data-lucide="play" class="w-4 h-4 mr-1"></i>
                    Test
                </button>
                <button class="btn-secondary py-2 px-3" style="font-size: 0.875rem;" onclick="viewResponses('${form.form_id}')">
                    <i data-lucide="bar-chart-3" class="w-4 h-4 mr-1"></i>
                    View
                </button>
            </div>
            
            <div class="grid grid-cols-3 gap-2">
                <button class="btn-secondary py-2 px-2" style="font-size: 0.75rem;" onclick="editForm('${form.form_id}')" title="Edit Form">
                    <i data-lucide="edit" class="w-3 h-3 mr-1"></i>
                    Edit
                </button>
                <button class="btn-secondary py-2 px-2" style="font-size: 0.75rem;" onclick="shareForm('${form.form_id}')" title="Share Form">
                    <i data-lucide="share" class="w-3 h-3 mr-1"></i>
                    Share
                </button>
                <button class="py-2 px-2 border rounded" style="font-size: 0.75rem; border-color: var(--error); color: var(--error); background: white;" onclick="deleteForm('${form.form_id}')" title="Delete Form">
                    <i data-lucide="trash-2" class="w-3 h-3 mr-1"></i>
                    Delete
                </button>
            </div>
        </div>
    `).join('');
    
    // Re-initialize icons
    lucide.createIcons();
}

function resetFormBuilder() {
    // Clear text dump
    const textDump = document.getElementById('textDump');
    if (textDump) textDump.value = '';
    
    // Clear form title
    const formTitle = document.getElementById('formTitle');
    if (formTitle) formTitle.value = '';
    
    // Hide form builder, show form creation step
    const formBuilder = document.getElementById('formBuilder');
    if (formBuilder) formBuilder.classList.add('hidden');
    
    const formCreationStep = document.getElementById('formCreationStep');
    if (formCreationStep) formCreationStep.classList.remove('hidden');
    
    // Clear current form data and editing state
    currentFormData = null;
    window.currentEditingFormId = null;
    
    // Reset progress indicators
    updateProgress(0);
}

function handleUrlRouting() {
    const path = window.location.pathname;
    
    if (path.startsWith('/form/')) {
        const formId = path.split('/form/')[1];
        if (formId) {
            showChat(formId);
        } else {
            showPage('landingPage');
        }
    } else if (path === '/dashboard') {
        if (currentUser) {
            showDashboard();
        } else {
            showPage('landingPage');
        }
    } else if (path === '/create') {
        if (currentUser) {
            showCreateForm();
        } else {
            showPage('landingPage');
        }
    } else if (currentUser && path === '/') {
        showDashboard();
    } else {
        showPage('landingPage');
    }
}

// Global initialization flag
let isAppInitialized = false;

function initializeApp() {
    if (isAppInitialized) return;
    isAppInitialized = true;
    
    console.log('🚀 Initializing Bermuda app...');
    
    // 1. Hide all pages initially except landing - using both display and hidden class
    const pages = ['dashboardPage', 'createFormPage', 'chatPage'];
    pages.forEach(pageId => {
        const element = document.getElementById(pageId);
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
        }
    });
    
    // 2. Hide all nested form elements as well
    const nestedElements = ['formCreationStep', 'formBuilder'];
    nestedElements.forEach(elementId => {
        const element = document.getElementById(elementId);
        if (element) {
            element.style.display = 'none';
            element.classList.add('hidden');
        }
    });
    
    // 3. Show landing page initially
    const landingPage = document.getElementById('landingPage');
    if (landingPage) {
        landingPage.style.display = 'block';
        landingPage.classList.remove('hidden');
    }
    
    // 4. Set up all event listeners
    setupEventListeners();
    
    // 5. Initialize authentication
    setupAuthentication();
    
    // 6. Initialize Lucide icons
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    console.log('✅ App initialization complete');
}

function setupEventListeners() {
    // Logo button - navbar click behavior
    const logoBtn = document.getElementById('logoBtn');
    if (logoBtn) {
        logoBtn.addEventListener('click', () => {
            if (currentUser) {
                showDashboard();
            } else {
                // Scroll to hero section on landing page
                const heroSection = document.querySelector('#landingPage section');
                if (heroSection) {
                    heroSection.scrollIntoView({ behavior: 'smooth' });
                } else {
                    showPage('landingPage');
                }
            }
        });
    }

    // Dashboard button - post-login navigation
    const dashboardBtn = document.getElementById('dashboardBtn');
    if (dashboardBtn) {
        dashboardBtn.addEventListener('click', showDashboard);
    }

    // Logout button - post-login
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            auth.signOut();
        });
    }

    // Landing page buttons
    const getStartedBtn = document.getElementById('getStartedBtn');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', () => {
            if (currentUser) {
                showCreateForm();
            } else {
                signInWithGoogle();
            }
        });
    }

    const viewDemoBtn = document.getElementById('viewDemoBtn');
    if (viewDemoBtn) {
        viewDemoBtn.addEventListener('click', () => {
            showChat('test-form-123');
        });
    }

    const navGetStarted = document.getElementById('navGetStarted');
    if (navGetStarted) {
        navGetStarted.addEventListener('click', () => {
            if (currentUser) {
                showCreateForm();
            } else {
                signInWithGoogle();
            }
        });
    }

    const finalCtaBtn = document.getElementById('finalCtaBtn');
    if (finalCtaBtn) {
        finalCtaBtn.addEventListener('click', () => {
            if (currentUser) {
                showCreateForm();
            } else {
                signInWithGoogle();
            }
        });
    }

    const emptyStateCreateBtn = document.getElementById('emptyStateCreateBtn');
    if (emptyStateCreateBtn) {
        emptyStateCreateBtn.addEventListener('click', showCreateForm);
    }
    
    // Dashboard and form creation
    const createFormBtn = document.getElementById('createFormBtn');
    if (createFormBtn) {
        createFormBtn.addEventListener('click', showCreateForm);
    }
    
    const backToDashboard = document.getElementById('backToDashboard');
    if (backToDashboard) {
        backToDashboard.addEventListener('click', showDashboard);
    }
    
    const inferFormBtn = document.getElementById('inferFormBtn');
    if (inferFormBtn) {
        inferFormBtn.addEventListener('click', inferFormFromText);
    }
    
    const saveFormBtn = document.getElementById('saveFormBtn');
    if (saveFormBtn) {
        saveFormBtn.addEventListener('click', saveForm);
    }
    
    const previewFormBtn = document.getElementById('previewFormBtn');
    if (previewFormBtn) {
        previewFormBtn.addEventListener('click', previewForm);
    }
    
    // Chat and modals
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const message = e.target.value.trim();
                if (message) {
                    e.target.value = '';
                    updateCharCount();
                    sendMessage(message);
                }
            }
        });
        
        chatInput.addEventListener('input', updateCharCount);
    }

    const sendMessageBtn = document.getElementById('sendMessageBtn');
    if (sendMessageBtn) {
        sendMessageBtn.addEventListener('click', () => {
            const input = document.getElementById('chatInput');
            if (input) {
                const message = input.value.trim();
                if (message) {
                    input.value = '';
                    updateCharCount();
                    sendMessage(message);
                }
            }
        });
    }

    const copyLinkBtn = document.getElementById('copyLinkBtn');
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', copyShareLink);
    }

    const closeShareModal = document.getElementById('closeShareModal');
    if (closeShareModal) {
        closeShareModal.addEventListener('click', () => {
            const modal = document.getElementById('shareModal');
            if (modal) {
                modal.classList.add('hidden');
            }
        });
    }

    const closePreviewModal = document.getElementById('closePreviewModal');
    if (closePreviewModal) {
        closePreviewModal.addEventListener('click', () => {
            const modal = document.getElementById('previewModal');
            if (modal) {
                modal.classList.add('hidden');
            }
        });
    }
    
    // Text dump counter
    const textDump = document.getElementById('textDump');
    if (textDump) {
        textDump.addEventListener('input', updateTextDumpCount);
    }
    
    console.log('✅ Event listeners attached');
}

function updateTextDumpCount() {
    const textDump = document.getElementById('textDump');
    const counter = document.getElementById('textDumpCount');
    if (textDump && counter) {
        counter.textContent = textDump.value.length;
    }
}

function updateCharCount() {
    const input = document.getElementById('chatInput');
    const count = document.getElementById('charCount');
    if (input && count) {
        count.textContent = `${input.value.length}/1000 characters`;
    }
}

function useExampleTopic(text) {
    const textDump = document.getElementById('textDump');
    if (textDump) {
        textDump.value = text;
        updateTextDumpCount();
        textDump.focus();
    }
}

function addNewQuestion() {
    if (!currentFormData) {
        currentFormData = { questions: [], demographics: [] };
    }
    
    const newQuestion = {
        text: '',
        type: 'text',
        enabled: true,
        options: []
    };
    
    currentFormData.questions.push(newQuestion);
    renderQuestions(currentFormData.questions);
    updateQuestionCount();
}

function removeQuestion(index) {
    if (currentFormData && currentFormData.questions[index]) {
        currentFormData.questions.splice(index, 1);
        renderQuestions(currentFormData.questions);
        updateQuestionCount();
    }
}

function toggleAllDemographics(enabled) {
    if (currentFormData && currentFormData.demographics) {
        currentFormData.demographics.forEach(demo => {
            demo.enabled = enabled;
        });
        renderDemographics(currentFormData.demographics);
    }
}

function updateProgress(step) {
    // Update step indicators
    const steps = ['step1', 'step2', 'step3'];
    const progressBars = ['progressBar1', 'progressBar2'];
    
    steps.forEach((stepId, index) => {
        const stepElement = document.getElementById(stepId);
        if (stepElement) {
            const circle = stepElement.querySelector('div');
            if (index < step) {
                // Completed step
                circle.className = 'w-10 h-10 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-semibold shadow-lg';
                stepElement.className = 'flex items-center space-x-3 step-indicator completed';
            } else if (index === step) {
                // Active step
                circle.className = 'w-10 h-10 text-white rounded-full flex items-center justify-center text-sm font-semibold shadow-lg';
                circle.style.backgroundColor = '#CC5500';
                stepElement.className = 'flex items-center space-x-3 step-indicator active';
            } else {
                // Future step
                circle.className = 'w-10 h-10 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center text-sm font-semibold';
                stepElement.className = 'flex items-center space-x-3 step-indicator';
            }
        }
    });
    
    // Update progress bars
    progressBars.forEach((barId, index) => {
        const bar = document.getElementById(barId);
        if (bar) {
            bar.style.width = index < step ? '100%' : '0%';
        }
    });
}

function displayFormBuilder(formData) {
    const formBuilder = document.getElementById('formBuilder');
    if (formBuilder) {
        formBuilder.style.display = 'block';
        formBuilder.classList.remove('hidden');
    }
    document.getElementById('formTitle').value = formData.title || '';
    
    // Update progress to step 2
    updateProgress(1);
    
    // Render questions
    renderQuestions(formData.questions || []);
    updateQuestionCount();
    
    // Render demographics
    renderDemographics(formData.demographics || []);
    
    // Re-initialize icons after displaying form builder
    lucide.createIcons();
    
    // Scroll to form builder
    document.getElementById('formBuilder').scrollIntoView({ behavior: 'smooth' });
}

function renderFormCard(form) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-2xl shadow-lg border border-gray-200 p-8 hover:shadow-xl hover:border-primary-300 transition-all duration-300 group relative transform hover:-translate-y-1';
    
    const createdDate = new Date(form.created_at).toLocaleDateString();
    const responseCount = form.response_count || 0;
    
    card.innerHTML = `
        <div class="flex items-start justify-between mb-4">
            <div class="flex-1 min-w-0">
                <h3 class="font-bold text-lg text-gray-900 mb-1 group-hover:text-primary-600 transition-colors truncate">${form.title}</h3>
                <p class="text-xs text-gray-500">Created ${createdDate}</p>
            </div>
            <div class="flex items-center px-2 py-1 rounded-full text-xs font-semibold ${form.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}">
                ${form.status === 'active' ? 'Active' : 'Draft'}
            </div>
        </div>
        
        <div class="grid grid-cols-2 gap-3 mb-4">
            <div class="text-center p-2 bg-gray-50 rounded-lg">
                <div class="text-xl font-bold text-primary-600">${responseCount}</div>
                <div class="text-xs text-gray-600">Responses</div>
            </div>
            <div class="text-center p-2 bg-gray-50 rounded-lg">
                <div class="text-xl font-bold text-gray-700">~3min</div>
                <div class="text-xs text-gray-600">Duration</div>
            </div>
        </div>
        
        <div class="flex flex-wrap gap-2 mb-4">
            <span class="px-3 py-1 rounded-full text-xs font-medium bg-primary-50 text-primary-600">Conversational</span>
            <span class="px-3 py-1 rounded-full text-xs font-medium bg-green-50 text-green-600">AI-powered</span>
        </div>
        
        <div class="flex gap-3">
            <button class="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-primary-600 border border-primary-200 rounded-lg hover:bg-primary-50 transition-all duration-200" onclick="testChat('${form.form_id}')">
                <i data-lucide="play" class="w-4 h-4 mr-1"></i>
                Test
            </button>
            <button class="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-primary-600 border border-primary-200 rounded-lg hover:bg-primary-50 transition-all duration-200" onclick="viewResponses('${form.form_id}')">
                <i data-lucide="bar-chart-3" class="w-4 h-4 mr-1"></i>
                Results
            </button>
        </div>
        
        <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-100">
            <div class="flex items-center space-x-1">
                <button class="p-1 text-gray-400 hover:text-primary-600 rounded hover:bg-primary-50 transition-all duration-200" onclick="editForm('${form.form_id}')" title="Edit Form">
                    <i data-lucide="edit-2" class="w-4 h-4"></i>
                </button>
                <button class="p-1 text-gray-400 hover:text-primary-600 rounded hover:bg-primary-50 transition-all duration-200" onclick="shareForm('${form.form_id}')" title="Share Form">
                    <i data-lucide="share" class="w-4 h-4"></i>
                </button>
            </div>
            <button class="p-1 text-gray-400 hover:text-red-600 rounded hover:bg-red-50 transition-all duration-200" onclick="deleteForm('${form.form_id}')" title="Delete Form">
                <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
        </div>
    `;
    
    return card;
}