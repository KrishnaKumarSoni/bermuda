function testChat(formId) {
    // Open form in chat mode for testing
    showChat(formId);
}

async function initializeChat(formId) {
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

async function sendMessage(message) {
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

function addMessageToChat(role, text) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    
    const isBot = role === 'bot';
    messageDiv.className = `flex ${isBot ? 'justify-start' : 'justify-end'} chat-message-enter`;
    
    const timestamp = formatTimestamp(new Date());
    
    messageDiv.innerHTML = `
        <div class="${isBot ? 'message-bot' : 'message-user'} max-w-xs sm:max-w-md">
            <div class="text-sm">${text}</div>
            <div class="text-xs opacity-70 mt-1">${timestamp}</div>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function pauseChat() {
    if (!currentChatSession) return;
    
    showLoading();
    
    try {
        const response = await fetch('https://us-central1-bermuda-01.cloudfunctions.net/api/chat-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                form_id: currentChatSession.formId,
                session_id: currentChatSession.sessionId,
                message: 'i want to pause for now, continue later',
                device_id: getDeviceId()
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to pause chat');
        }
        
        const result = await response.json();
        
        // Add bot response about pausing
        if (result.response) {
            addMessageToChat('bot', result.response);
            messageCount++;
            updateMessageCount();
        }
        
        showChatPaused();
        showToast('Chat paused! You can continue anytime.', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to pause chat. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function resumeChat() {
    if (!currentChatSession) return;
    
    showLoading();
    
    try {
        const response = await fetch('https://us-central1-bermuda-01.cloudfunctions.net/api/resume-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentChatSession.sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to resume chat');
        }
        
        const result = await response.json();
        
        // Add resume message to chat
        if (result.response) {
            addMessageToChat('bot', result.response);
            messageCount++;
            updateMessageCount();
        }
        
        // Show chat input again
        document.getElementById('chatPaused').classList.add('hidden');
        document.getElementById('chatInputContainer').classList.remove('hidden');
        
        showToast('Chat resumed! Continue where you left off.', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to resume chat. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}