// Form creation functions
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

function showCreateForm() {
    showPage('createFormPage');
    resetFormBuilder();
    // Show the form creation step, hide form builder initially - this is handled by showPage now
    // but we need to ensure formBuilder stays hidden initially
    const formBuilder = document.getElementById('formBuilder');
    if (formBuilder) {
        formBuilder.style.display = 'none';
        formBuilder.classList.add('hidden');
    }
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

function renderQuestions(questions) {
    const questionsList = document.getElementById('questionsList');
    questionsList.innerHTML = '';
    
    questions.forEach((question, index) => {
        const questionCard = createQuestionCard(question, index);
        questionsList.appendChild(questionCard);
    });
    
    // Re-initialize icons after rendering questions
    lucide.createIcons();
}

function renderDemographics(demographics) {
    const demographicsList = document.getElementById('demographicsList');
    demographicsList.innerHTML = '';
    
    demographics.forEach((demo, index) => {
        const demoCard = createDemographicCard(demo, index);
        demographicsList.appendChild(demoCard);
    });
    
    // Re-initialize icons after rendering demographics
    lucide.createIcons();
}

function updateQuestion(index, field, value) {
    if (currentFormData && currentFormData.questions[index]) {
        currentFormData.questions[index][field] = value;
    }
}

function updateQuestionCount() {
    const questionCount = document.getElementById('questionCount');
    if (questionCount && currentFormData) {
        const enabledQuestions = currentFormData.questions.filter(q => q.enabled !== false).length;
        questionCount.textContent = enabledQuestions;
    }
}