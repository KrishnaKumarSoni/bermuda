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