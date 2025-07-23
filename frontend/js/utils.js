function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    let bgColor, textColor;
    
    if (type === 'success') {
        bgColor = 'var(--success)';
        textColor = 'white';
    } else if (type === 'error') {
        bgColor = 'var(--error)';
        textColor = 'white';
    } else {
        bgColor = 'var(--primary)';
        textColor = 'white';
    }
    
    toast.className = 'px-6 py-4 rounded font-body font-bold';
    toast.style.backgroundColor = bgColor;
    toast.style.color = textColor;
    toast.style.boxShadow = 'none';
    toast.textContent = message;
    
    document.getElementById('toastContainer').appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

function showLoading() {
    document.getElementById('loadingSpinner').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingSpinner').classList.add('hidden');
}

function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function formatTimestamp(date) {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}