function initializeChat(formId) {
    showLoading();
    
    try {
        // Get form data
        const response = await fetch(`https://us-central1-bermuda-01.cloudfunctions.net/api/forms/${formId}`);
        
        if (!response.ok) {
            throw new Error('Form not found');
        }
        
        const formData = await response.json();
        currentFormData = formData;
        
        // Update UI
        document.getElementById('chatFormTitle').textContent = formData.title;
        
        // Initialize chat session
        currentChatSession = {
            sessionId: generateSessionId(),
            formId: formId,
            messages: []
        };
        
        // Clear messages
        document.getElementById('chatMessages').innerHTML = '';
        messageCount = 0;
        updateMessageCount();
        
        // Start conversation
        await sendMessage('');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to load form. Please check the link.', 'error');
        showPage('landingPage');
    } finally {
        hideLoading();
    }
}

function sendMessage(message) {
    if (!currentChatSession) return;
    
    // Add user message if not empty
    if (message.trim()) {
        addMessageToChat('user', message);
        messageCount++;
        updateMessageCount();
    }
    
    // Show typing indicator instead of loading screen
    showTypingIndicator();
    
    try {
        const response = await fetch('https://us-central1-bermuda-01.cloudfunctions.net/api/chat-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                form_id: currentChatSession.formId,
                session_id: currentChatSession.sessionId,
                message: message,
                device_id: getDeviceId(),
                location: 'Unknown'
            })
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('API Error:', response.status, errorText);
            throw new Error(`API Error: ${response.status} - ${errorText}`);
        }
        
        const result = await response.json();
        
        // Remove typing indicator and add bot response
        hideTypingIndicator();
        addMessageToChat('bot', result.response);
        messageCount++;
        updateMessageCount();
        
        // Check if chat is completed or paused
        if (result.completed) {
            showChatCompleted();
        } else if (result.paused) {
            showChatPaused();
        }
        
    } catch (error) {
        console.error('Error:', error);
        hideTypingIndicator();
        showToast('Failed to send message. Please try again.', 'error');
    }
}