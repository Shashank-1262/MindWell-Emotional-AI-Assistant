/**
 * MindWell Emotional Wellness App - Frontend JavaScript
 * Handles authentication, navigation, and API communication
 */

// API Configuration
const API_BASE = window.location.origin;
let authToken = localStorage.getItem('mindwell_token') || null;
let currentUser = localStorage.getItem('mindwell_user') || null;

// ==================== Utility Functions ====================

/**
 * Converts a basic markdown string into safe HTML.
 * Handles: **bold**, *italic*, numbered lists, bullet lists, and newlines.
 */
function parseMarkdown(text) {
    if (!text) return '';

    // Escape raw HTML to prevent XSS
    let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

    // Convert numbered list items (e.g. "1. Item") into <ol><li> blocks
    // Split by lines first
    const lines = html.split(/\n/);
    let result = [];
    let inOL = false;
    let inUL = false;

    for (let line of lines) {
        const olMatch = line.match(/^(\d+)\.\s+(.*)$/);
        const ulMatch = line.match(/^[-*]\s+(.*)$/);

        if (olMatch) {
            if (!inOL) { result.push('<ol>'); inOL = true; }
            if (inUL) { result.push('</ul>'); inUL = false; }
            result.push(`<li>${olMatch[2]}</li>`);
        } else if (ulMatch) {
            if (!inUL) { result.push('<ul>'); inUL = true; }
            if (inOL) { result.push('</ol>'); inOL = false; }
            result.push(`<li>${ulMatch[1]}</li>`);
        } else {
            if (inOL) { result.push('</ol>'); inOL = false; }
            if (inUL) { result.push('</ul>'); inUL = false; }
            // Non-list line: wrap in paragraph if non-empty
            if (line.trim() !== '') {
                result.push(`<p>${line}</p>`);
            }
        }
    }
    if (inOL) result.push('</ol>');
    if (inUL) result.push('</ul>');

    html = result.join('');

    // Bold: **text** or __text__
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/__(.+?)__/g, '<strong>$1</strong>');

    // Italic: *text* or _text_
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    html = html.replace(/_(.+?)_/g, '<em>$1</em>');

    return html;
}

function showLoader() {
    document.getElementById('loader').classList.remove('hidden');
}

function hideLoader() {
    document.getElementById('loader').classList.add('hidden');
}

function showError(elementId, message) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = message;
    errorEl.style.display = 'block';
}

function clearError(elementId) {
    const errorEl = document.getElementById(elementId);
    errorEl.textContent = '';
    errorEl.style.display = 'none';
}

// ==================== API Functions ====================

async function apiCall(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }

    if (body) {
        options.body = JSON.stringify(body);
    }

    console.log('API Call:', method, `${API_BASE}${endpoint}`);

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();

        console.log('API Response:', response.status, data);

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Call failed:', error);
        throw error;
    }
}

// ==================== Authentication ====================

async function handleLogin(event) {
    event.preventDefault();
    clearError('login-error');

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value.trim();

    console.log('Login attempt for username:', username);

    if (!username || !password) {
        showError('login-error', 'Please fill in all fields');
        return;
    }

    showLoader();

    try {
        console.log('Calling API...');
        const data = await apiCall('/auth/login', 'POST', { username, password });
        console.log('Login successful:', data);
        
        authToken = data.token;
        currentUser = data.user_id;
        
        localStorage.setItem('mindwell_token', authToken);
        localStorage.setItem('mindwell_user', currentUser);
        console.log('Token and user saved to localStorage');
        
        showApp();
    } catch (error) {
        console.error('Login error:', error);
        showError('login-error', error.message);
    } finally {
        hideLoader();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    clearError('register-error');

    const username = document.getElementById('register-username').value.trim();
    const password = document.getElementById('register-password').value.trim();

    if (!username || !password) {
        showError('register-error', 'Please fill in all fields');
        return;
    }

    if (password.length < 4) {
        showError('register-error', 'Password must be at least 4 characters');
        return;
    }

    showLoader();

    try {
        const data = await apiCall('/auth/register', 'POST', { username, password });
        
        authToken = data.token;
        currentUser = data.user_id;
        
        localStorage.setItem('mindwell_token', authToken);
        localStorage.setItem('mindwell_user', currentUser);
        
        showApp();
    } catch (error) {
        showError('register-error', error.message);
    } finally {
        hideLoader();
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('mindwell_token');
    localStorage.removeItem('mindwell_user');
    
    showAuthScreen();
}

// ==================== Screen Management ====================

function showAuthScreen() {
    document.getElementById('auth-screen').classList.add('active');
    document.getElementById('app-screen').classList.remove('active');
    
    // Clear forms
    document.getElementById('login-form').reset();
    document.getElementById('register-form').reset();
    clearError('login-error');
    clearError('register-error');
}

function showApp() {
    document.getElementById('auth-screen').classList.remove('active');
    document.getElementById('app-screen').classList.add('active');
    
    // Update user display
    document.getElementById('user-display').textContent = currentUser;
    
    // Load dashboard by default
    showView('dashboard');
}

// ==================== View Navigation ====================

function showView(viewName) {
    // Hide all views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    
    // Remove active state from nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected view
    document.getElementById(`${viewName}-view`).classList.add('active');
    
    // Activate corresponding nav link
    document.querySelector(`[data-view="${viewName}"]`)?.classList.add('active');
    
    // Load data for specific views
    if (viewName === 'dashboard') {
        loadDashboard();
    } else if (viewName === 'insights') {
        loadInsights();
    }
}

// ==================== Dashboard ====================

async function loadDashboard() {
    showLoader();
    
    try {
        const data = await apiCall('/dashboard');
        
        if (!data.hasData) {
            document.getElementById('no-data-message').classList.remove('hidden');
            document.getElementById('dashboard-content').classList.add('hidden');
        } else {
            document.getElementById('no-data-message').classList.add('hidden');
            document.getElementById('dashboard-content').classList.remove('hidden');
            
            // Update stats
            document.getElementById('stat-emotion').textContent = data.latest_emotion;
            document.getElementById('stat-stress').textContent = `${data.latest_stress}/10`;
            document.getElementById('stat-avg-stress').textContent = `${data.avg_recent_stress}/10`;
            document.getElementById('stat-total').textContent = data.total_logs;
            document.getElementById('latest-timestamp').textContent = `Last logged: ${data.latest_timestamp}`;
            
            // Update stress badge color
            const stressEl = document.getElementById('stat-stress');
            stressEl.className = 'stat-value';
            if (data.latest_stress <= 3) stressEl.style.color = 'var(--success)';
            else if (data.latest_stress <= 6) stressEl.style.color = 'var(--warning)';
            else stressEl.style.color = 'var(--danger)';
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    } finally {
        hideLoader();
    }
}

// ==================== Webcam Face Detection ====================

let webcamStream = null;
let capturedFaceImage = null;

async function startWebcam() {
    try {
        const video = document.getElementById('webcam-video');
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        
        webcamStream = stream;
        video.srcObject = stream;
        video.classList.add('active');
        
        // Enable/disable buttons
        document.getElementById('start-webcam-btn').disabled = true;
        document.getElementById('capture-face-btn').disabled = false;
        document.getElementById('stop-webcam-btn').disabled = false;
        
    } catch (error) {
        console.error('Error accessing webcam:', error);
        alert('Could not access webcam. Please ensure you have granted camera permissions.');
    }
}

function captureFrame() {
    const video = document.getElementById('webcam-video');
    const canvas = document.getElementById('webcam-canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    ctx.drawImage(video, 0, 0);
    
    // Get base64 image
    capturedFaceImage = canvas.toDataURL('image/jpeg', 0.8);
    
    // Show preview
    const preview = document.getElementById('face-preview');
    const previewImg = document.getElementById('captured-face');
    previewImg.src = capturedFaceImage;
    preview.classList.remove('hidden');
    
    console.log('Face captured successfully');
}

function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    
    const video = document.getElementById('webcam-video');
    video.srcObject = null;
    video.classList.remove('active');
    
    // Reset buttons
    document.getElementById('start-webcam-btn').disabled = false;
    document.getElementById('capture-face-btn').disabled = true;
    document.getElementById('stop-webcam-btn').disabled = true;
}

// ==================== Log My Day ====================

async function handleLogDay(event) {
    event.preventDefault();
    
    const text = document.getElementById('day-text').value.trim();
    
    if (!text) {
        alert('Please describe your day');
        return;
    }
    
    showLoader();
    
    try {
        // Prepare request data
        const requestData = { text };
        
        // Include face image if captured
        if (capturedFaceImage) {
            requestData.face_image = capturedFaceImage;
            console.log('Including face image in request');
        }
        
        const data = await apiCall('/log', 'POST', requestData);
        
        // Display emotion results
        displayEmotionResults(data.log);
        
        // Initialize chat with therapist's opening message
        initializeChat(data.therapist_message);
        
        // Clear form and reset webcam
        document.getElementById('day-text').value = '';
        capturedFaceImage = null;
        document.getElementById('face-preview').classList.add('hidden');
        stopWebcam();
        
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        hideLoader();
    }
}

function displayEmotionResults(log) {
    const resultsSection = document.getElementById('emotion-results');
    
    // Map emotions to emojis
    const emotionEmojis = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'surprised': '😲',
        'neutral': '😐',
        'fearful': '😨',
        'disgusted': '🤢'
    };
    
    // Update emotion display
    document.getElementById('result-emotion-icon').textContent = emotionEmojis[log.emotion] || '😊';
    document.getElementById('result-emotion').textContent = log.emotion;
    document.getElementById('result-stress').textContent = log.stress_level;
    document.getElementById('result-summary').textContent = log.summary;
    
    // Update stress badge color
    const stressBadge = document.getElementById('result-stress-badge');
    stressBadge.className = 'stress-badge';
    if (log.stress_level <= 3) stressBadge.classList.add('low');
    else if (log.stress_level <= 6) stressBadge.classList.add('medium');
    else stressBadge.classList.add('high');
    
    // Display triggers
    const triggersEl = document.getElementById('result-triggers');
    triggersEl.innerHTML = '';
    if (log.triggers && log.triggers.length > 0) {
        log.triggers.forEach(trigger => {
            const tag = document.createElement('span');
            tag.className = 'trigger-tag';
            tag.textContent = trigger;
            triggersEl.appendChild(tag);
        });
    }
    
    // Show face detection info if available
    if (log.face_detected && log.face_emotion) {
        const faceInfo = document.createElement('div');
        faceInfo.className = 'face-info';
        faceInfo.innerHTML = `
            <p><strong>📸 Face Expression Detected:</strong> ${log.face_emotion}</p>
            <p class="help-text">Combined text and facial analysis for more accurate results</p>
        `;
        triggersEl.parentElement.appendChild(faceInfo);
    }
    
    resultsSection.classList.remove('hidden');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function initializeChat(initialMessage) {
    const chatSection = document.getElementById('chat-section');
    const messagesContainer = document.getElementById('chat-messages');
    
    // Clear previous chat
    messagesContainer.innerHTML = '';
    
    // Add therapist's opening message
    addChatMessage('ai', initialMessage);
    
    // Show chat section
    chatSection.classList.remove('hidden');
    chatSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function addChatMessage(sender, text) {
    const messagesContainer = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'ai' ? '🤖' : '👤';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    if (sender === 'ai') {
        bubble.innerHTML = parseMarkdown(text);
    } else {
        bubble.textContent = text;
    }
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function handleChatSend() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Check if user wants to exit
    if (message.toLowerCase() === 'exit' || message.toLowerCase() === 'quit') {
        document.getElementById('chat-section').classList.add('hidden');
        input.value = '';
        return;
    }
    
    // Add user message to chat
    addChatMessage('user', message);
    input.value = '';
    
    showLoader();
    
    try {
        const data = await apiCall('/chat', 'POST', { message });
        
        // Add AI response
        addChatMessage('ai', data.response);
        
    } catch (error) {
        addChatMessage('ai', `Error: ${error.message}`);
    } finally {
        hideLoader();
    }
}

// ==================== History Q&A ====================

async function handleHistoryQA(event) {
    event.preventDefault();
    
    const question = document.getElementById('qa-question').value.trim();
    
    if (!question) {
        alert('Please enter a question');
        return;
    }
    
    showLoader();
    
    try {
        const data = await apiCall('/history-qa', 'POST', { question });
        
        // Display answer
        const resultsSection = document.getElementById('qa-results');
        document.getElementById('qa-answer').innerHTML = parseMarkdown(data.answer);
        resultsSection.classList.remove('hidden');
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert(`Error: ${error.message}`);
    } finally {
        hideLoader();
    }
}

// ==================== Insights ====================

async function loadInsights() {
    document.getElementById('insights-loading').classList.remove('hidden');
    document.getElementById('insights-content').classList.add('hidden');
    
    try {
        const data = await apiCall('/insights');
        
        // Update insight cards
        document.getElementById('insight-total').textContent = data.total_logs;
        document.getElementById('insight-avg-stress').textContent = `${data.avg_stress}/10`;
        document.getElementById('insight-emotion').textContent = data.dominant_emotion;
        document.getElementById('insight-trend').textContent = data.trend;
        document.getElementById('insight-trigger').textContent = data.common_trigger;
        document.getElementById('insights-text').textContent = data.insights_text;
        
        // Display recent logs
        const recentLogsContainer = document.getElementById('recent-logs');
        recentLogsContainer.innerHTML = '';
        
        if (data.recent_logs && data.recent_logs.length > 0) {
            data.recent_logs.forEach(log => {
                const logItem = document.createElement('div');
                logItem.className = 'log-item';
                
                logItem.innerHTML = `
                    <div class="log-item-header">
                        <span class="log-item-emotion">${log.final_emotion}</span>
                        <span class="log-item-stress">Stress: ${log.stress_level}/10</span>
                    </div>
                    <div class="log-item-text">${log.user_text.substring(0, 100)}${log.user_text.length > 100 ? '...' : ''}</div>
                    <div class="log-item-time">${log.timestamp}</div>
                `;
                
                recentLogsContainer.appendChild(logItem);
            });
        } else {
            document.getElementById('recent-logs-section').style.display = 'none';
        }
        
        document.getElementById('insights-loading').classList.add('hidden');
        document.getElementById('insights-content').classList.remove('hidden');
        
    } catch (error) {
        console.error('Error loading insights:', error);
        document.getElementById('insights-loading').innerHTML = '<p>Error loading insights. Please try again.</p>';
    }
}

// ==================== Event Listeners ====================

document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    if (authToken && currentUser) {
        showApp();
    } else {
        showAuthScreen();
    }
    
    // Auth tab switching
    document.querySelectorAll('.auth-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            
            // Update tabs
            document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update forms
            document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
            document.getElementById(`${targetTab}-form`).classList.add('active');
            
            // Clear errors
            clearError('login-error');
            clearError('register-error');
        });
    });
    
    // Auth forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    
    // Logout
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            const view = link.dataset.view;
            showView(view);
        });
    });
    
    // Log My Day form
    document.getElementById('log-form').addEventListener('submit', handleLogDay);
    
    // Webcam controls
    document.getElementById('start-webcam-btn').addEventListener('click', startWebcam);
    document.getElementById('capture-face-btn').addEventListener('click', captureFrame);
    document.getElementById('stop-webcam-btn').addEventListener('click', stopWebcam);
    
    // Chat
    document.getElementById('chat-send-btn').addEventListener('click', handleChatSend);
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleChatSend();
        }
    });
    
    // History Q&A form
    document.getElementById('qa-form').addEventListener('submit', handleHistoryQA);
});

// ==================== Initialize ====================

console.log('MindWell Emotional Wellness App - Frontend Loaded');
