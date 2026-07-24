/* ===========================================================================
   CineBrain AI - Client Application JavaScript
   =========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const sidebar = document.getElementById('sidebar');
    const menuToggle = document.getElementById('menuToggle');
    const newChatBtn = document.getElementById('newChatBtn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    const historyList = document.getElementById('historyList');
    
    const chatTitle = document.getElementById('chatTitle');
    const activeModelBadge = document.getElementById('activeModelBadge');
    const sessionCostBadge = document.getElementById('sessionCostBadge');
    const chatMessages = document.getElementById('chatMessages');
    const welcomeScreen = document.getElementById('welcomeScreen');
    
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    
    const modelSelect = document.getElementById('modelSelect');
    const tempSlider = document.getElementById('tempSlider');
    const tempValue = document.getElementById('tempValue');
    const tokensSlider = document.getElementById('tokensSlider');
    const tokensValue = document.getElementById('tokensValue');

    // State Variables
    let currentSessionId = null;
    let isGenerating = false;

    // ---------------------------------------------------------------------------
    // Event Listeners
    // ---------------------------------------------------------------------------

    // Settings Sliders
    tempSlider.addEventListener('input', (e) => tempValue.textContent = e.target.value);
    tokensSlider.addEventListener('input', (e) => tokensValue.textContent = e.target.value);
    modelSelect.addEventListener('change', (e) => activeModelBadge.textContent = e.target.value);

    // Mobile Sidebar Toggle
    menuToggle.addEventListener('click', () => sidebar.classList.toggle('open'));

    // New Chat Button
    newChatBtn.addEventListener('click', () => startNewChat());

    // Clear All History
    clearAllBtn.addEventListener('click', async () => {
        if (confirm('Bạn có chắc chắn muốn xóa toàn bộ lịch sử trò chuyện?')) {
            await fetch('/api/sessions', { method: 'DELETE' });
            startNewChat();
            loadHistoryList();
        }
    });

    // Auto-resize Textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = (userInput.scrollHeight) + 'px';
    });

    // Handle Enter to Send (Shift+Enter for new line)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Quick Prompt Cards Click
    document.querySelectorAll('.prompt-card').forEach(card => {
        card.addEventListener('click', () => {
            const promptText = card.getAttribute('data-prompt');
            if (promptText && !isGenerating) {
                userInput.value = promptText;
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // Form Submit Chat Handler
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text || isGenerating) return;

        // Reset input box
        userInput.value = '';
        userInput.style.height = 'auto';

        // Send Message
        await sendMessage(text);
    });

    // Initialize App
    loadHistoryList();

    // ---------------------------------------------------------------------------
    // Main Functions
    // ---------------------------------------------------------------------------

    async function loadHistoryList() {
        try {
            const res = await fetch('/api/sessions');
            const sessions = await res.json();
            
            historyList.innerHTML = '';
            if (sessions.length === 0) {
                historyList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; padding: 8px;">Chưa có lịch sử</div>';
                return;
            }

            sessions.forEach(s => {
                const item = document.createElement('div');
                item.className = `history-item ${s.id === currentSessionId ? 'active' : ''}`;
                item.innerHTML = `
                    <div class="history-item-info">
                        <i class="fa-solid fa-film"></i>
                        <span class="history-item-title">${escapeHtml(s.title)}</span>
                    </div>
                    <button class="delete-session-btn" title="Xóa phiên này">
                        <i class="fa-solid fa-xmark"></i>
                    </button>
                `;

                // Select session
                item.addEventListener('click', (e) => {
                    if (!e.target.closest('.delete-session-btn')) {
                        loadSession(s.id);
                        if (window.innerWidth <= 768) sidebar.classList.remove('open');
                    }
                });

                // Delete session
                const deleteBtn = item.querySelector('.delete-session-btn');
                deleteBtn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    await fetch(`/api/sessions/${s.id}`, { method: 'DELETE' });
                    if (currentSessionId === s.id) {
                        startNewChat();
                    }
                    loadHistoryList();
                });

                historyList.appendChild(item);
            });
        } catch (err) {
            console.error('Lỗi tải lịch sử:', err);
        }
    }

    async function loadSession(sessionId) {
        try {
            const res = await fetch(`/api/sessions/${sessionId}`);
            if (!res.ok) return;

            const session = await res.json();
            currentSessionId = session.id;
            chatTitle.textContent = session.title || 'Cuộc trò chuyện điện ảnh';
            sessionCostBadge.textContent = `$${(session.total_cost || 0).toFixed(4)}`;

            // Clear chat window & hide welcome
            chatMessages.innerHTML = '';
            welcomeScreen.style.display = 'none';

            // Render Messages
            session.messages.forEach(msg => {
                appendMessageUI(msg.role, msg.content, msg.cost_info, msg.latency);
            });

            loadHistoryList();
        } catch (err) {
            console.error('Lỗi khi mở phiên chat:', err);
        }
    }

    function startNewChat() {
        currentSessionId = null;
        chatTitle.textContent = 'CineBrain - Trợ lý Điện ảnh';
        sessionCostBadge.textContent = '$0.0000';
        chatMessages.innerHTML = '';
        chatMessages.appendChild(welcomeScreen);
        welcomeScreen.style.display = 'flex';
        loadHistoryList();
    }

    async function sendMessage(messageText) {
        isGenerating = true;
        sendBtn.disabled = true;

        // Hide welcome screen if showing
        if (welcomeScreen.parentNode === chatMessages) {
            welcomeScreen.style.display = 'none';
        }

        // Render User Message
        appendMessageUI('user', messageText);

        // Render Bot Streaming Message Placeholder
        const botMsgObj = appendMessageUI('assistant', '', null, null, true);
        const bubble = botMsgObj.bubble;
        const metricsContainer = botMsgObj.metricsContainer;

        let fullText = '';

        try {
            const response = await fetch('/api/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSessionId,
                    message: messageText,
                    model: modelSelect.value,
                    temperature: parseFloat(tempSlider.value),
                    top_p: 0.9,
                    max_tokens: parseInt(tokensSlider.value)
                })
            });

            if (!response.ok) {
                throw new Error('Lỗi kết nối API');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop(); // keep last buffer chunk

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const jsonStr = line.replace('data: ', '').trim();
                        if (!jsonStr) continue;

                        try {
                            const data = JSON.parse(jsonStr);

                            if (data.type === 'chunk') {
                                fullText += data.content;
                                bubble.innerHTML = typeof marked !== 'undefined' 
                                    ? marked.parse(fullText) 
                                    : escapeHtml(fullText);
                                scrollToBottom();
                            } else if (data.type === 'done') {
                                currentSessionId = data.session_id;
                                chatTitle.textContent = data.title;
                                
                                // Update session cost badge
                                const costInfo = data.cost_info || {};
                                metricsContainer.innerHTML = `
                                    <span><i class="fa-solid fa-bolt"></i> ${data.latency}s</span>
                                    <span><i class="fa-solid fa-font"></i> ${data.total_tokens} tokens</span>
                                    <span><i class="fa-solid fa-tag"></i> $${(costInfo.total_cost || 0).toFixed(5)}</span>
                                `;

                                // Refresh history sidebar
                                loadHistoryList();
                                // Fetch updated session total cost
                                updateSessionTotalCost(currentSessionId);
                            }
                        } catch (err) {
                            console.error('Error parsing SSE data:', err);
                        }
                    }
                }
            }
        } catch (err) {
            bubble.innerHTML = `<span style="color: #ef4444;"><i class="fa-solid fa-triangle-exclamation"></i> Có lỗi xảy ra: ${escapeHtml(err.message)}</span>`;
        } finally {
            isGenerating = false;
            sendBtn.disabled = false;
        }
    }

    async function updateSessionTotalCost(sessionId) {
        try {
            const res = await fetch(`/api/sessions/${sessionId}`);
            if (res.ok) {
                const s = await res.json();
                sessionCostBadge.textContent = `$${(s.total_cost || 0).toFixed(4)}`;
            }
        } catch (e) {}
    }

    function appendMessageUI(role, text, costInfo = null, latency = null, isStreaming = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role === 'user' ? 'user' : 'bot'}`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        avatarDiv.innerHTML = role === 'user' 
            ? '<i class="fa-solid fa-user"></i>' 
            : '<i class="fa-solid fa-clapperboard"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'bubble';

        if (isStreaming) {
            bubbleDiv.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
        } else {
            bubbleDiv.innerHTML = (role === 'assistant' && typeof marked !== 'undefined')
                ? marked.parse(text)
                : escapeHtml(text);
        }

        contentDiv.appendChild(bubbleDiv);

        const metricsContainer = document.createElement('div');
        metricsContainer.className = 'message-metrics';

        if (role === 'assistant' && costInfo) {
            metricsContainer.innerHTML = `
                <span><i class="fa-solid fa-bolt"></i> ${latency || 0}s</span>
                <span><i class="fa-solid fa-font"></i> ${(costInfo.prompt_tokens + costInfo.completion_tokens) || 0} tokens</span>
                <span><i class="fa-solid fa-tag"></i> $${(costInfo.total_cost || 0).toFixed(5)}</span>
            `;
        }

        contentDiv.appendChild(metricsContainer);

        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        chatMessages.appendChild(messageDiv);
        scrollToBottom();

        return { messageDiv, bubble: bubbleDiv, metricsContainer };
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(str) {
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
