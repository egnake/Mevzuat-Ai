/**
 * Mevzuat-AI Frontend Application
 */

const state = {
    files: [],
    filePaths: [],
    fileNames: [],
    isAnalyzed: false,
    isLoading: false
};

const elements = {
    uploadZone: document.getElementById('uploadZone'),
    fileInput: document.getElementById('fileInput'),
    fileList: document.getElementById('fileList'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    chatInput: document.getElementById('chatInput'),
    sendBtn: document.getElementById('sendBtn'),
    chatContainer: document.getElementById('chatContainer'),
    welcomeScreen: document.getElementById('welcomeScreen'),
    messages: document.getElementById('messages'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    loadingText: document.getElementById('loadingText'),
    toastContainer: document.getElementById('toastContainer')
};

document.addEventListener('DOMContentLoaded', () => {
    initializeUpload();
    initializeChat();
    loadSystemInfo();
});

function initializeUpload() {
    elements.uploadZone.addEventListener('click', (e) => {
        // Prevent opening dialog twice if clicking the button/label
        if (e.target.closest('.upload-btn') || e.target === elements.fileInput) return;
        elements.fileInput.click();
    });

    elements.fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

    // Drag & Drop
    elements.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.add('dragover');
    });

    elements.uploadZone.addEventListener('dragleave', () => {
        elements.uploadZone.classList.remove('dragover');
    });

    elements.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        elements.uploadZone.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    elements.analyzeBtn.addEventListener('click', analyzeDocuments);
}

function handleFiles(fileList) {
    const validFiles = Array.from(fileList).filter(f => f.type === 'application/pdf');
    if (validFiles.length === 0) {
        showToast('Sadece PDF dosyaları yüklenebilir.', 'warning');
        return;
    }
    state.files = [...state.files, ...validFiles];
    updateFileList();
    elements.analyzeBtn.disabled = state.files.length === 0;
}

function updateFileList() {
    elements.fileList.innerHTML = state.files.map((file, index) => `
        <div class="file-item">
            <div class="file-item-info">
                <i class="fa-regular fa-file-pdf"></i>
                <span class="file-item-name" title="${file.name}">${file.name}</span>
            </div>
            <button class="file-item-remove" onclick="removeFile(${index})">
                <i class="fa-solid fa-times"></i>
            </button>
        </div>
    `).join('');
}

function removeFile(index) {
    state.files.splice(index, 1);
    updateFileList();
    elements.analyzeBtn.disabled = state.files.length === 0;
}

async function analyzeDocuments() {
    if (state.files.length === 0) return;
    showLoading('PDF dosyaları yükleniyor...');

    try {
        const formData = new FormData();
        state.files.forEach(file => formData.append('files', file));

        const uploadResponse = await fetch('/api/upload', { method: 'POST', body: formData });
        const uploadData = await uploadResponse.json();

        if (!uploadData.success) throw new Error(uploadData.error);

        state.filePaths = uploadData.paths;
        state.fileNames = uploadData.filenames;

        updateLoadingText('Analiz ediliyor...');
        const analyzeResponse = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: state.filePaths, filenames: state.fileNames })
        });

        const analyzeData = await analyzeResponse.json();
        if (!analyzeData.success) throw new Error(analyzeData.error);

        state.isAnalyzed = true;
        hideLoading();
        showToast(`${analyzeData.chunks} parça indekslendi.`, 'success');
        elements.sendBtn.disabled = false;

    } catch (error) {
        hideLoading();
        let errorMsg = error.message;
        if (error.message.includes('Failed to fetch')) {
            errorMsg = 'Sunucuya erişilemiyor. Lütfen uygulamanın çalıştığından emin olun (python app.py).';
        }
        showToast(errorMsg, 'error');
    }
}

function initializeChat() {
    elements.sendBtn.addEventListener('click', sendMessage);
    elements.chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

async function sendMessage() {
    const question = elements.chatInput.value.trim();
    if (!question) return;
    if (!state.isAnalyzed) {
        showToast('Lütfen önce analiz yapın.', 'warning');
        return;
    }

    if (elements.welcomeScreen) elements.welcomeScreen.style.display = 'none';

    addMessage('user', question);
    elements.chatInput.value = '';
    elements.sendBtn.disabled = true;

    const loadingId = addMessage('assistant', 'Thought', [], true);

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        const data = await response.json();

        removeMessage(loadingId);

        if (!data.success) throw new Error(data.error);
        addMessage('assistant', data.answer, data.sources);

    } catch (error) {
        removeMessage(loadingId);
        let errorMsg = error.message;
        if (error.message.includes('Failed to fetch')) {
            errorMsg = 'Sunucu ile iletişim kurulamadı. Uygulamanın açık olduğundan emin olun.';
        }
        addMessage('assistant', `Hata: ${errorMsg}`);
    }
    elements.sendBtn.disabled = false;
}

function addMessage(role, content, sources = [], isLoading = false) {
    const id = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    const avatar = role === 'user' ? '<i class="fa-solid fa-user"></i>' : '<i class="fa-solid fa-scale-balanced"></i>';

    let contentHtml = `<div class="message-text">${isLoading ? '<i class="fa-solid fa-circle-notch fa-spin"></i> Yanıtlanıyor...' : escapeHtml(content)}</div>`;

    if (sources.length > 0) {
        contentHtml += `
            <button class="sources-toggle" onclick="toggleSources('${id}')">
                <i class="fa-solid fa-book"></i> Kaynaklar (${sources.length}) <i class="fa-solid fa-chevron-down"></i>
            </button>
            <div class="sources-list" id="sources-${id}">
                ${sources.map(s => `
                    <div class="source-card">
                        <div class="source-header">
                            <span class="source-badge">Belge ${s.id}</span>
                            <span class="source-file">Sayfa ${s.page} - ${s.file}</span>
                        </div>
                        <div class="source-preview">${escapeHtml(s.preview)}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    const html = `
        <div class="message ${role}" id="${id}">
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">${contentHtml}</div>
        </div>
    `;

    elements.messages.insertAdjacentHTML('beforeend', html);
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

function toggleSources(id) {
    const list = document.getElementById(`sources-${id}`);
    if (list) {
        list.classList.toggle('open');
    }
}

function showLoading(text) {
    elements.loadingText.textContent = text;
    elements.loadingOverlay.classList.add('active');
}

function updateLoadingText(text) {
    elements.loadingText.textContent = text;
}

function hideLoading() {
    elements.loadingOverlay.classList.remove('active');
}

function showToast(msg, type = 'success') {
    const icons = {
        success: '<i class="fa-solid fa-check-circle"></i>',
        error: '<i class="fa-solid fa-exclamation-circle"></i>',
        warning: '<i class="fa-solid fa-triangle-exclamation"></i>'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `${icons[type]} <span>${msg}</span>`;

    elements.toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function loadSystemInfo() {
    fetch('/api/system-info')
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                document.getElementById('modelName').textContent = data.model;
                document.getElementById('chunkSize').textContent = data.chunk_size;
                document.getElementById('topK').textContent = data.top_k;
            }
        })
        .catch(console.error);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

window.removeFile = removeFile;
window.toggleSources = toggleSources;
