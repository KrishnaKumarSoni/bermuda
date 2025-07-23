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

function createQuestionCard(question, index) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-2xl shadow-lg border border-gray-200 p-8 hover:shadow-xl hover:border-primary-300 transition-all duration-300 group relative';
    
    const typeOptions = [
        { value: 'text', label: 'Text Response', icon: 'type' },
        { value: 'multiple_choice', label: 'Multiple Choice', icon: 'list' },
        { value: 'yes_no', label: 'Yes/No', icon: 'check-circle' },
        { value: 'rating', label: 'Rating (1-5)', icon: 'star' },
        { value: 'number', label: 'Number', icon: 'hash' }
    ];
    
    const currentType = typeOptions.find(t => t.value === question.type) || typeOptions[0];
    
    card.innerHTML = `
        <!-- Header with drag handle and controls -->
        <div class="flex flex-wrap items-start justify-between gap-4 mb-6">
            <div class="flex items-center space-x-3">
                <div class="drag-handle cursor-move opacity-0 group-hover:opacity-100 transition-opacity">
                    <i data-lucide="grip-vertical" class="w-5 h-5 text-gray-400"></i>
                </div>
                <div class="w-10 h-10 bg-gradient-to-r from-primary-500 to-orange-500 text-white rounded-2xl flex items-center justify-center text-sm font-bold shadow-lg">
                    ${index + 1}
                </div>
                <div>
                    <div class="font-bold text-gray-900 text-lg">Question ${index + 1}</div>
                    <div class="text-sm text-gray-600 flex items-center space-x-2">
                        <i data-lucide="${currentType.icon}" class="w-3 h-3"></i>
                        <span>${currentType.label}</span>
                    </div>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                <label class="inline-flex items-center cursor-pointer group/toggle">
                    <input type="checkbox" class="sr-only peer" ${question.enabled !== false ? 'checked' : ''} 
                           onchange="toggleQuestion(${index}, this.checked)">
                    <div class="relative w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-primary-300 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full peer-checked:bg-primary-600"></div>
                </label>
                <button class="opacity-0 group-hover:opacity-100 transition-opacity p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50" 
                        onclick="removeQuestion(${index})" title="Remove Question">
                    <i data-lucide="trash-2" class="w-4 h-4"></i>
                </button>
            </div>
        </div>
        
        <!-- Question Content -->
        <div class="space-y-6">
            <div>
                <label class="block text-lg font-semibold text-gray-900 mb-3">Question Text</label>
                <textarea 
                    class="w-full border-2 border-gray-200 rounded-2xl p-4 resize-none text-lg focus:border-primary-500 focus:ring-4 focus:ring-primary-200 transition-all duration-200" 
                    rows="2"
                    placeholder="What would you like to ask?" 
                    onchange="updateQuestion(${index}, 'text', this.value)">${question.text || ''}</textarea>
            </div>
            
            <div class="grid grid-cols-1 ${(question.type === 'multiple_choice' || question.type === 'rating') ? 'lg:grid-cols-2' : ''} gap-4">
                <div>
                    <label class="block text-lg font-semibold text-gray-900 mb-3">Question Type</label>
                    <select class="w-full border-2 border-gray-200 rounded-2xl p-4 text-lg focus:border-primary-500 focus:ring-4 focus:ring-primary-200 transition-all duration-200" onchange="updateQuestion(${index}, 'type', this.value)">
                        ${typeOptions.map(option => `
                            <option value="${option.value}" ${question.type === option.value ? 'selected' : ''}>
                                ${option.label}
                            </option>
                        `).join('')}
                    </select>
                </div>
                ${(question.type === 'multiple_choice' || question.type === 'rating') ? `
                <div>
                    <label class="block text-lg font-semibold text-gray-900 mb-3">
                        ${question.type === 'rating' ? 'Scale Labels (optional)' : 'Answer Options'}
                    </label>
                    <input type="text" 
                           class="w-full border-2 border-gray-200 rounded-2xl p-4 text-lg focus:border-primary-500 focus:ring-4 focus:ring-primary-200 transition-all duration-200" 
                            placeholder="${question.type === 'rating' ? 'Poor, Fair, Good, Great, Excellent' : 'Option 1, Option 2, Option 3'}" 
                            value="${(question.options || []).join(', ')}"
                            onchange="updateQuestion(${index}, 'options', this.value.split(',').map(s => s.trim()).filter(s => s))">
                </div>
                ` : ''}
            </div>
            
            <!-- Question Preview -->
            <div class="bg-primary-50 rounded-2xl p-6 border-l-4 border-primary-500">
                <div class="text-sm font-bold text-primary-700 mb-2">PREVIEW</div>
                <div class="text-lg text-gray-800">${question.text || 'Question preview will appear here'}</div>
            </div>
        </div>
    `;
    
    return card;
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

function createDemographicCard(demo, index) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-2xl shadow-lg border border-gray-200 p-8 hover:shadow-xl hover:border-primary-300 transition-all duration-300';
    
    const demographicIcons = {
        'age': 'calendar',
        'gender': 'user',
        'location': 'map-pin',
        'education': 'graduation-cap',
        'income': 'dollar-sign',
        'occupation': 'briefcase',
        'ethnicity': 'users'
    };
    
    const iconName = demographicIcons[demo.name.toLowerCase()] || 'user-check';
    
    card.innerHTML = `
        <div class="space-y-4">
            <div class="flex flex-wrap items-center justify-between">
                <div class="flex items-center space-x-3">
                    <div class="w-12 h-12 bg-primary-100 rounded-2xl flex items-center justify-center">
                        <i data-lucide="${iconName}" class="w-5 h-5 text-primary-600"></i>
                    </div>
                    <div>
                        <div class="font-bold text-gray-900 text-lg">${demo.name}</div>
                        <div class="text-sm text-gray-600">${demo.type}</div>
                    </div>
                </div>
                <label class="inline-flex items-center cursor-pointer">
                    <input type="checkbox" class="sr-only peer" ${demo.enabled ? 'checked' : ''} 
                           onchange="toggleDemographic(${index}, this.checked)">
                    <div class="relative w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-primary-300 after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:after:translate-x-full peer-checked:bg-primary-600"></div>
                </label>
            </div>
            <div class="text-sm text-gray-600 leading-relaxed">
                ${getDemographicDescription(demo.name)}
            </div>
        </div>
    `;
    
    return card;
}

function updateQuestion(index, field, value) {
    if (currentFormData && currentFormData.questions[index]) {
        currentFormData.questions[index][field] = value;
    }
}

function toggleQuestion(index, enabled) {
    if (currentFormData && currentFormData.questions[index]) {
        currentFormData.questions[index].enabled = enabled;
    }
}

function toggleDemographic(index, enabled) {
    if (currentFormData && currentFormData.demographics[index]) {
        currentFormData.demographics[index].enabled = enabled;
    }
}

function getCurrentFormData() {
    if (!currentFormData) {
        return { questions: [], demographics: [], title: '' };
    }
    
    // Get the current title from the input
    const titleInput = document.getElementById('formTitle');
    const title = titleInput ? titleInput.value.trim() : '';
    
    return {
        ...currentFormData,
        title: title
    };
}

function previewForm() {
    const formData = getCurrentFormData();
    if (!formData.questions || formData.questions.length === 0) {
        showToast('Please add some questions before previewing', 'error');
        return;
    }
    
    // Create a temporary form data and show it in a new tab
    const previewData = {
        ...formData,
        id: 'preview',
        title: formData.title || 'Preview Form'
    };
    
    // Generate preview URL
    const previewUrl = `/form/preview?data=${encodeURIComponent(JSON.stringify(previewData))}`;
    window.open(previewUrl, '_blank');
}

async function saveForm() {
    if (!currentUser) {
        showToast('Please sign in to save forms', 'error');
        return;
    }
    
    // Check if we're editing an existing form
    const isEditing = window.currentEditingFormId;
    
    // Get title
    const title = document.getElementById('formTitle').value.trim();
    if (!title) {
        showToast('Please enter a form title', 'error');
        return;
    }
    
    // Validate we have current form data
    if (!currentFormData) {
        showToast('No form data available', 'error');
        return;
    }
    
    // Prepare form data
    const formData = {
        title: title,
        questions: currentFormData.questions || [],
        demographics: currentFormData.demographics || []
    };
    
    // Validate we have at least one enabled question
    const enabledQuestions = formData.questions.filter(q => q.enabled !== false);
    if (enabledQuestions.length === 0) {
        showToast('Please enable at least one question', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const token = await currentUser.getIdToken();
        
        let response;
        if (isEditing) {
            // Update existing form
            response = await fetch(`https://us-central1-bermuda-01.cloudfunctions.net/api/forms/${window.currentEditingFormId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });
        } else {
            // Create new form
            response = await fetch('https://us-central1-bermuda-01.cloudfunctions.net/api/save-form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || 'Failed to save form');
        }
        
        const result = await response.json();
        
        if (isEditing) {
            showToast(result.message || 'Form updated successfully!', 'success');
            // Clear editing state
            clearFormBuilderState();
            // Go back to dashboard
            showDashboard();
        } else {
            showToast(result.message || 'Form saved successfully!', 'success');
            
            // Show share modal or redirect to dashboard
            if (result.form_id) {
                const shareUrl = `${window.location.origin}/form/${result.form_id}`;
                // Just show a toast with the URL for now, then redirect to dashboard
                showToast('Form created! Share link copied to clipboard.', 'success');
                
                // Copy URL to clipboard
                if (navigator.clipboard) {
                    navigator.clipboard.writeText(shareUrl);
                }
                
                // Redirect to dashboard after a short delay
                setTimeout(() => {
                    showDashboard();
                }, 2000);
            } else {
                showDashboard();
            }
        }
        
    } catch (error) {
        console.error('Save form error:', error);
        showToast(`Failed to save form: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function updateQuestionCount() {
    const questionCount = document.getElementById('questionCount');
    if (questionCount && currentFormData) {
        const enabledQuestions = currentFormData.questions.filter(q => q.enabled !== false).length;
        questionCount.textContent = enabledQuestions;
    }
}