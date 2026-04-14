// ═══════════════════════════════════════════════════════════════
// CONSOLIDATED RESUME AI APP - Refactored & DRY
// Universal functions replacing repetitive code patterns
// ═══════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════
// GLOBAL VARIABLES & CONSTANTS
// ═══════════════════════════════════════════════════════════════

const API_BASE = 'http://localhost:5000/api';
const RESUME_MODES = { MAIN: 'main', POLISH: 'polish', TAILOR: 'tailor' };

// Global state
let currentSessionId = null;
let currentFilename = null;
let resumesData = [];
let currentTailoredContent = null;
let currentPolishIntensity = 'medium';
let currentPdfDoc = null;
let currentPdfPage = 1;
let currentPdfScale = 1.5;

// Mode-specific state manager
const resumeState = {
    [RESUME_MODES.MAIN]: {
        selectedId: null,
        previewElementId: 'resumePreview',
        listElementId: 'resumeList'
    },
    [RESUME_MODES.POLISH]: {
        selectedId: null,
        previewElementId: 'polishOriginalPreview',
        listElementId: 'polishResumeList',
        tailoredPreviewElementId: 'polishPolishedPreview'
    },
    [RESUME_MODES.TAILOR]: {
        selectedId: null,
        previewElementId: 'tailorOriginalPreview',
        listElementId: 'tailorResumeList',
        tailoredPreviewElementId: 'tailorTailoredPreview'
    }
};

// Initialize on page load
window.addEventListener('DOMContentLoaded', async () => {
    await initResumeMode(RESUME_MODES.MAIN);
});

// ═══════════════════════════════════════════════════════════════
// UNIVERSAL RESUME DATA MANAGEMENT
// ═══════════════════════════════════════════════════════════════

/**
 * Initialize resume system for a specific mode
 */
async function initResumeMode(mode) {
    console.log(`[INIT] Starting initResumeMode for mode: ${mode}`);
    await loadResumesFromFolder();
    console.log(`[INIT] resumesData after load:`, resumesData);
    renderResumeListForMode(mode);
    console.log(`[INIT] Rendered list for mode: ${mode}`);
}

/**
 * Load all resumes from server folder
 */
async function loadResumesFromFolder() {
    try {
        console.log(`[LOAD] Fetching from ${API_BASE}/list-resumes`);
        const response = await fetch(`${API_BASE}/list-resumes`);
        const data = await response.json();
        
        console.log(`[LOAD] Response OK: ${response.ok}, Has resumes: ${!!data.resumes}, Resumes: `, data);

        if (response.ok && data.resumes) {
            const filtered = data.resumes.filter(f => !f.name.endsWith('.json'));
            console.log(`[LOAD] After filter: ${filtered.length} resumes`);
            
            resumesData = filtered.map(fileInfo => {
                const stored = getStoredResume(fileInfo.name);
                return {
                    id: stored?.id || Date.now() + Math.random(),
                    name: fileInfo.name,
                    filename: fileInfo.name,
                    content: stored?.content || null,
                    uploadDate: new Date(fileInfo.modified * 1000).toLocaleDateString(),
                    scores: stored?.scores || null,
                    isGrading: false
                };
            });
            console.log(`✓ Loaded ${resumesData.length} resumes from folder`, resumesData);
        } else {
            console.warn(`[LOAD] No resumes in response`, data);
            resumesData = [];
        }
    } catch (error) {
        console.error('Error loading resumes:', error);
        resumesData = [];
    }
}

/**
 * Universal: Get resume by ID
 */
function getResumeById(resumeId) {
    return resumesData.find(r => r.id === resumeId);
}

/**
 * Get stored resume metadata from localStorage
 */
function getStoredResume(filename) {
    try {
        const stored = localStorage.getItem('resumesData');
        if (stored) {
            const all = JSON.parse(stored);
            return all.find(r => r.filename === filename);
        }
    } catch (e) {
        // Silently fail - corruption is ok
    }
    return null;
}

/**
 * Save resumes to localStorage
 */
function saveResumesToStorage() {
    const toSave = resumesData.map(r => ({
        id: r.id, name: r.name, filename: r.filename,
        content: r.content, uploadDate: r.uploadDate,
        scores: r.scores, isGrading: r.isGrading
    }));
    localStorage.setItem('resumesData', JSON.stringify(toSave));
}

/**
 * Universal: Load resume content from backend
 */
function loadResumeContent(resumeId) {
    const resume = getResumeById(resumeId);
    if (!resume) return Promise.reject(new Error('Resume not found'));
    if (resume.content) return Promise.resolve(resume.content);

    if (!resume.filename) {
        return Promise.reject(new Error('Resume file reference lost'));
    }

    return fetch(`${API_BASE}/get-resume?filename=${encodeURIComponent(resume.filename)}`)
        .then(r => {
            if (!r.ok) throw new Error('Failed to load resume');
            return r.text();
        })
        .then(content => {
            if (!content?.trim()) throw new Error('File is empty');
            resume.content = content;
            saveResumesToStorage();
            return content;
        });
}

/**
 * Universal: Save resume content (update or new file)
 */
async function saveResumeContent(filename, content, newName = null) {
    if (newName) {
        // Show loading state
        const statusEl = document.createElement('div');
        statusEl.id = 'pdf-save-status';
        statusEl.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(20, 20, 20, 0.95);
            color: #F5F0E8;
            padding: 30px 50px;
            border-radius: 12px;
            border: 1px solid #C9A84C;
            z-index: 10000;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8);
            font-size: 16px;
        `;
        statusEl.innerHTML = `
            <div style="margin-bottom: 20px;">
                <div style="font-size: 32px; margin-bottom: 12px;">⏳</div>
                <div>Generating PDF...</div>
                <div style="font-size: 12px; color: #C9A84C; margin-top: 8px;">This may take up to 30 seconds</div>
            </div>
        `;
        document.body.appendChild(statusEl);
        
        try {
            // Save as new PDF file with timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout
            
            const response = await fetch(`${API_BASE}/save-resume-pdf`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    filename: newName,
                    resume_text: content 
                }),
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Failed to save');
            return data.filename;
        } finally {
            // Remove loading state
            const el = document.getElementById('pdf-save-status');
            if (el) el.remove();
        }
    } else {
        // Update existing file
        const response = await fetch(`${API_BASE}/update-resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename, content })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Failed to update');

        const resume = resumesData.find(r => r.filename === filename);
        if (resume) {
            resume.content = content;
            saveResumesToStorage();
        }
        return filename;
    }
}

/**
 * Universal: Delete resume from storage and backend
 */
async function deleteResume(resumeId) {
    const resume = getResumeById(resumeId);
    if (!resume || !confirm(`Delete "${resume.name}"? This cannot be undone.`)) return;

    try {
        const response = await fetch(
            `${API_BASE}/delete-resume?filename=${encodeURIComponent(resume.filename)}`,
            { method: 'DELETE' }
        );
        if (!response.ok) throw new Error('Failed to delete');

        // Clear from all modes
        Object.values(resumeState).forEach(state => {
            if (state.selectedId === resumeId) {
                state.selectedId = null;
                clearPreviewElement(state.previewElementId);
            }
        });

        await loadResumesFromFolder();
        Object.keys(RESUME_MODES).forEach(key => 
            renderResumeListForMode(RESUME_MODES[key])
        );
        console.log('Resume deleted:', resume.name);
    } catch (error) {
        alert('Failed to delete resume: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════════
// UNIVERSAL UI RENDERING
// ═══════════════════════════════════════════════════════════════

/**
 * Universal: Render resume list for mode
 */
function renderResumeListForMode(mode) {
    const state = resumeState[mode];
    const container = document.getElementById(state.listElementId);
    console.log(`[RENDER] Mode: ${mode}, Container ID: ${state.listElementId}, Found: ${!!container}, Data length: ${resumesData.length}`);
    
    if (!container) {
        console.error(`[RENDER] Container not found for mode ${mode}`);
        return;
    }

    if (!resumesData.length) {
        console.log(`[RENDER] No resumes in data, showing empty state`);
        container.innerHTML = getEmptyStateHTML(
            '📋', 'No resumes yet', 'Upload to get started'
        );
        return;
    }

    console.log(`[RENDER] Rendering ${resumesData.length} resumes`);
    container.innerHTML = resumesData.map(resume => `
        <div class="resume-card ${state.selectedId === resume.id ? 'active' : ''}" 
             onclick="selectResumeForMode('${mode}', ${resume.id})">
            <div class="resume-card-title">${resume.name}</div>
            ${mode === RESUME_MODES.MAIN ? `
                <div class="resume-card-meta">
                    <span>${resume.uploadDate}</span>
                    <span>${resume.scores ? '✓ Graded' : '•'}</span>
                </div>
            ` : ''}
        </div>
    `).join('');
}

/**
 * Universal: Select and display resume for a mode
 */
function selectResumeForMode(mode, resumeId) {
    const state = resumeState[mode];
    const resume = getResumeById(resumeId);
    if (!resume) return;

    state.selectedId = resumeId;
    currentFilename = resume.filename;
    renderResumeListForMode(mode);

    loadResumeContent(resumeId)
        .then(() => displayResumeForMode(mode, resumeId))
        .catch(error => showErrorInElement(state.previewElementId, error.message));
}

/**
 * Display resume based on file type and mode
 */
function displayResumeForMode(mode, resumeId) {
    const resume = getResumeById(resumeId);
    const state = resumeState[mode];
    const previewEl = document.getElementById(state.previewElementId);
    const fileExt = resume.filename.split('.').pop().toLowerCase();

    // For POLISH mode, always use text display (extract PDF text if needed)
    if (mode === RESUME_MODES.POLISH && fileExt === 'pdf') {
        // Show loading state
        previewEl.innerHTML = getPlaceholderHTML('Extracting text from PDF...', '⏳');
        
        // Fetch extracted text from backend
        fetch(`${API_BASE}/get-resume-text?filename=${encodeURIComponent(resume.filename)}`)
            .then(r => {
                if (!r.ok) throw new Error('Failed to extract text');
                return r.json();
            })
            .then(data => {
                // Display extracted text
                const pre = document.createElement('pre');
                pre.className = 'resume-text';
                pre.style.cssText = 'white-space: pre-wrap; word-wrap: break-word; font-size: 12px; line-height: 1.6; margin: 0;';
                pre.textContent = data.content;
                previewEl.innerHTML = '';
                previewEl.appendChild(pre);
                
                // Cache the extracted content
                resume.content = data.content;
                
                // Show polish button
                document.getElementById('polishBtn')?.setAttribute('style', 'display: inline-block');
                resetTailoredPreview(mode);
            })
            .catch(error => showErrorInElement(state.previewElementId, error.message));
    } else if (fileExt === 'pdf' && mode !== RESUME_MODES.POLISH) {
        // PDF preview for MAIN and TAILOR modes
        displayPdf(resume.filename, state.previewElementId)
            .then(() => {
                if (mode === RESUME_MODES.MAIN) {
                    document.getElementById('actionButtons')?.setAttribute('style', 'display: flex');
                    updateGradingPanel(resume);
                } else if (mode === RESUME_MODES.TAILOR) {
                    resetTailoredPreview(mode);
                }
            })
            .catch(error => showErrorInElement(state.previewElementId, error.message));
    } else {
        // Text display for all non-PDF files
        const pre = document.createElement('pre');
        pre.className = 'resume-text';
        pre.style.cssText = 'white-space: pre-wrap; word-wrap: break-word; font-size: 12px; line-height: 1.6; margin: 0;';
        pre.textContent = resume.content;
        previewEl.innerHTML = '';
        previewEl.appendChild(pre);

        if (mode === RESUME_MODES.MAIN) {
            document.getElementById('actionButtons')?.setAttribute('style', 'display: flex');
            updateGradingPanel(resume);
        } else if (mode === RESUME_MODES.POLISH) {
            // For Polish mode, show polish button
            document.getElementById('polishBtn')?.setAttribute('style', 'display: inline-block');
            resetTailoredPreview(mode);
        } else {
            resetTailoredPreview(mode);
        }
    }
}

/**
 * Reset tailored preview for mode
 */
function resetTailoredPreview(mode) {
    const state = resumeState[mode];
    if (!state.tailoredPreviewElementId) return;
    
    const el = document.getElementById(state.tailoredPreviewElementId);
    if (el) {
        const msg = mode === RESUME_MODES.POLISH 
            ? 'Polish Resume button to see results'
            : 'Tailor Resume to see results';
        el.innerHTML = getPlaceholderHTML(msg, '✨', false);
    }
}

/**
 * Generate empty state HTML
 */
function getEmptyStateHTML(icon, title, subtitle) {
    return `
        <div class="empty-state">
            <div class="empty-state-icon">${icon}</div>
            <div>${title}</div>
            <div style="font-size: 11px; margin-top: 4px;">${subtitle}</div>
        </div>
    `;
}

/**
 * Generate placeholder HTML (loading/error)
 */
function getPlaceholderHTML(message, icon = '⏳', isError = false, animate = !isError) {
    const style = animate ? ' animation: spin 2s linear infinite;' : '';
    const color = isError ? 'color: #e74c3c;' : '';
    const size = isError ? '36px' : '32px';
    
    return `
        <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column;">
            <div style="font-size: ${size}; margin-bottom: 12px;${style}${color}">${icon}</div>
            <div style="color: var(--text-muted); text-align: center;">${message}</div>
        </div>
    `;
}

/**
 * Show error in element
 */
function showErrorInElement(elementId, message) {
    const el = document.getElementById(elementId);
    if (el) el.innerHTML = getPlaceholderHTML(message, '✕', true);
}

/**
 * Clear preview element
 */
function clearPreviewElement(elementId) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = getPlaceholderHTML('Select a resume to preview', '👼', false);
    }
}

// ═══════════════════════════════════════════════════════════════
// UNIVERSAL STATUS & API FUNCTIONS
// ═══════════════════════════════════════════════════════════════

/**
 * Universal: Show status message
 */
function showStatus(elementId, message, type) {
    const el = document.getElementById(elementId);
    if (el) {
        el.innerHTML = `<div class="status ${type}">${message}</div>`;
        el.style.display = 'block';
    }
}

/**
 * Universal: Hide status message
 */
function hideStatus(elementId, delay = 0) {
    if (delay > 0) {
        setTimeout(() => hideStatus(elementId), delay);
        return;
    }
    const el = document.getElementById(elementId);
    if (el) el.style.display = 'none';
}

/**
 * Universal: API call with status reporting
 */
async function callApi(endpoint, payload, statusElementId = null, loadingMsg = 'Processing...') {
    try {
        if (statusElementId) showStatus(statusElementId, loadingMsg, 'loading');

        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || `Error: ${response.status}`);

        if (statusElementId) {
            showStatus(statusElementId, '✓ Success!', 'success');
            hideStatus(statusElementId, 3000);
        }
        return data;
    } catch (error) {
        if (statusElementId) {
            showStatus(statusElementId, `Error: ${error.message}`, 'error');
        }
        throw error;
    }
}

// ═══════════════════════════════════════════════════════════════
// PANEL NAVIGATION
// ═══════════════════════════════════════════════════════════════

async function switchPanel(panelId, button) {
    console.log(`[SWITCH] Switching to panel: ${panelId}`);
    
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    document.getElementById(panelId).classList.add('active');
    button.classList.add('active');

    if (panelId === 'panel-my-resumes') {
        console.log(`[SWITCH] Initializing MAIN mode`);
        await initResumeMode(RESUME_MODES.MAIN);
    } else if (panelId === 'panel-bullet-polish') {
        console.log(`[SWITCH] Initializing POLISH mode`);
        await initResumeMode(RESUME_MODES.POLISH);
    } else if (panelId === 'panel-job-tailor') {
        console.log(`[SWITCH] Initializing TAILOR mode`);
        await initResumeMode(RESUME_MODES.TAILOR);
    }
    
    console.log(`[SWITCH] Panel switch complete`);
}

function switchTab(tabId, button) {
    const container = button.closest('.tab-container').parentElement;
    container.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    container.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    button.classList.add('active');
}

// ═══════════════════════════════════════════════════════════════
// PDF VIEWER (Consolidated)
// ═══════════════════════════════════════════════════════════════

async function renderPdfPage(pdfDoc, pageNum, canvas, ctx) {
    const page = await pdfDoc.getPage(pageNum);
    const viewport = page.getViewport({ scale: currentPdfScale });
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    await page.render({ canvasContext: ctx, viewport }).promise;
}

async function displayPdf(filename, elementId = 'resumePreview') {
    const preview = document.getElementById(elementId);
    preview.innerHTML = getPlaceholderHTML('Loading PDF...');

    try {
        const response = await fetch(`${API_BASE}/get-resume?filename=${encodeURIComponent(filename)}`);
        if (!response.ok) throw new Error('Failed to load PDF');

        const arrayBuffer = await response.arrayBuffer();
        currentPdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        currentPdfPage = 1;

        preview.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; gap: 10px;">
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 6px; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button onclick="previousPdfPage()" style="padding: 6px 12px; background: var(--gold); color: var(--dark); border: none; border-radius: 4px; cursor: pointer;">← Previous</button>
                        <input id="pdfPageNum" type="number" value="1" min="1" max="${currentPdfDoc.numPages}" style="width: 50px; padding: 6px; border: 1px solid var(--gold); background: var(--dark-3); color: var(--cream); border-radius: 4px; text-align: center;">
                        <span style="color: var(--text-muted);">of ${currentPdfDoc.numPages}</span>
                        <button onclick="nextPdfPage()" style="padding: 6px 12px; background: var(--gold); color: var(--dark); border: none; border-radius: 4px; cursor: pointer;">Next →</button>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button onclick="zoomPdfOut()" style="padding: 6px 12px; background: rgba(201,168,76,0.5); border: 1px solid var(--gold); border-radius: 4px; cursor: pointer;">−</button>
                        <span id="pdfZoomLevel" style="color: var(--text-muted); min-width: 50px; text-align: center;">150%</span>
                        <button onclick="zoomPdfIn()" style="padding: 6px 12px; background: rgba(201,168,76,0.5); border: 1px solid var(--gold); border-radius: 4px; cursor: pointer;">+</button>
                    </div>
                </div>
                <div style="flex: 1; overflow-y: auto; display: flex; justify-content: center; background: rgba(0,0,0,0.5); border-radius: 6px; padding: 10px;">
                    <canvas id="pdfCanvas" style="max-width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border-radius: 4px;"></canvas>
                </div>
            </div>
        `;

        document.getElementById('pdfPageNum').addEventListener('change', (e) => goToPdfPage(parseInt(e.target.value)));
        
        const canvas = document.getElementById('pdfCanvas');
        await renderPdfPage(currentPdfDoc, currentPdfPage, canvas, canvas.getContext('2d'));
    } catch (error) {
        throw error;
    }
}

async function nextPdfPage() {
    if (currentPdfDoc && currentPdfPage < currentPdfDoc.numPages) {
        currentPdfPage++;
        await updatePdfDisplay();
    }
}

async function previousPdfPage() {
    if (currentPdfDoc && currentPdfPage > 1) {
        currentPdfPage--;
        await updatePdfDisplay();
    }
}

async function goToPdfPage(pageNum) {
    if (currentPdfDoc && pageNum > 0 && pageNum <= currentPdfDoc.numPages) {
        currentPdfPage = pageNum;
        await updatePdfDisplay();
    }
}

async function updatePdfDisplay() {
    const canvas = document.getElementById('pdfCanvas');
    const pageInput = document.getElementById('pdfPageNum');
    await renderPdfPage(currentPdfDoc, currentPdfPage, canvas, canvas.getContext('2d'));
    pageInput.value = currentPdfPage;
}

function zoomPdfIn() {
    currentPdfScale += 0.25;
    updatePdfZoom();
}

function zoomPdfOut() {
    if (currentPdfScale > 0.5) currentPdfScale -= 0.25;
    updatePdfZoom();
}

async function updatePdfZoom() {
    const canvas = document.getElementById('pdfCanvas');
    const page = await currentPdfDoc.getPage(currentPdfPage);
    const viewport = page.getViewport({ scale: currentPdfScale });
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
    document.getElementById('pdfZoomLevel').textContent = Math.round(currentPdfScale * 66.67) + '%';
}

// ═══════════════════════════════════════════════════════════════
// MAIN MODE: GRADING & OPERATIONS
// ═══════════════════════════════════════════════════════════════

function gradeSelectedResume() {
    const state = resumeState[RESUME_MODES.MAIN];
    if (!state.selectedId) {
        alert('Please select a resume first');
        return;
    }

    const resume = getResumeById(state.selectedId);
    if (!resume || resume.isGrading) return;

    if (resume.filename?.toLowerCase().endsWith('.txt')) {
        if (resume.content) {
            performGradeResume(resume);
        } else {
            loadResumeContent(state.selectedId)
                .then(() => performGradeResume(getResumeById(state.selectedId)))
                .catch(e => console.error('Error:', e));
        }
    } else {
        performGradeResume(resume);
    }
}

function performGradeResume(resume) {
    resume.isGrading = true;
    const gradingContent = document.getElementById('gradingContent');
    gradingContent.innerHTML = getPlaceholderHTML(
        resume.filename?.endsWith('.pdf') 
            ? 'Extracting text from PDF...'
            : 'Analyzing resume...'
    );

    fetch(`${API_BASE}/grade-resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: resume.filename, resume_text: resume.content })
    })
    .then(r => r.json().then(d => [r, d]))
    .then(([r, data]) => {
        resume.isGrading = false;
        if (!r.ok) throw new Error(data.error || 'Grading failed');

        resume.scores = {
            overall: Math.round(data.scores.overall),
            ats: Math.round(data.scores.ats_score),
            sections: Math.round(data.scores.sections_score),
            bullets: Math.round(data.scores.bullets_score),
            feedback: `Keywords: ${data.scores.keywords_score}/100 - ${data.scores.feedback || 'Resume analyzed'}`
        };
        saveResumesToStorage();
        updateGradingPanel(resume);
        renderResumeListForMode(RESUME_MODES.MAIN);
    })
    .catch(error => {
        resume.isGrading = false;
        gradingContent.innerHTML = getPlaceholderHTML(
            `Error: ${error.message}`, '❌', true
        ) + '<button class="btn-grade" onclick="gradeSelectedResume()" style="margin-top: 16px;">Retry</button>';
    });
}

function updateGradingPanel(resume) {
    const gradingContent = document.getElementById('gradingContent');
    if (!resume.scores) {
        gradingContent.innerHTML = getEmptyStateHTML('📊', 'No scores yet', 'Grade this resume');
        return;
    }

    const getScoreClass = (score) => score >= 75 ? 'high' : score >= 50 ? 'medium' : 'low';
    const s = resume.scores;

    gradingContent.innerHTML = `
        <div class="score-section">
            <h4>📈 Overall Metrics</h4>
            <div class="score-grid">
                <div class="score-item">
                    <div class="score-item-label">Overall Score</div>
                    <div class="score-item-value ${getScoreClass(s.overall)}">${s.overall}</div>
                </div>
                <div class="score-item">
                    <div class="score-item-label">ATS Compatibility</div>
                    <div class="score-item-value ${getScoreClass(s.ats)}">${s.ats}</div>
                </div>
            </div>
        </div>
        <div class="score-section">
            <h4>🔍 Detailed Breakdown</h4>
            <div class="score-grid">
                <div class="score-item">
                    <div class="score-item-label">Sections Quality</div>
                    <div class="score-item-value ${getScoreClass(s.sections)}">${s.sections}</div>
                </div>
                <div class="score-item">
                    <div class="score-item-label">Bullet Points</div>
                    <div class="score-item-value ${getScoreClass(s.bullets)}">${s.bullets}</div>
                </div>
            </div>
        </div>
        ${s.feedback ? `
            <div class="score-section">
                <h4>💡 Feedback</h4>
                <div style="background: var(--dark-3); padding: 12px; border-radius: 6px; border-left: 3px solid var(--gold); font-size: 12px; line-height: 1.6;">
                    ${s.feedback}
                </div>
            </div>
        ` : ''}
    `;
}

function downloadResumePDF() {
    const state = resumeState[RESUME_MODES.MAIN];
    if (!state.selectedId) {
        alert('Please select a resume first');
        return;
    }

    const resume = getResumeById(state.selectedId);
    if (!resume?.content) return;

    const element = document.createElement('a');
    element.href = URL.createObjectURL(new Blob([resume.content], { type: 'text/plain' }));
    element.download = resume.name.replace(/\.[^/.]+$/, '') + '_graded.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// ═══════════════════════════════════════════════════════════════
// POLISH RESUME MODE
// ═══════════════════════════════════════════════════════════════

/**
 * Select polish intensity and update button states
 */
function selectPolishIntensity(intensity) {
    currentPolishIntensity = intensity;
    document.querySelectorAll('[data-intensity]').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-intensity="${intensity}"]`).classList.add('active');
}

/**
 * Polish resume with selected intensity
 */
async function polishResume() {
    const state = resumeState[RESUME_MODES.POLISH];
    if (!state.selectedId) {
        alert('Please select a resume first');
        return;
    }

    const resume = getResumeById(state.selectedId);
    if (!resume) return;

    const polishedEl = document.getElementById(state.tailoredPreviewElementId);
    polishedEl.innerHTML = getPlaceholderHTML('Polishing resume with ' + currentPolishIntensity + ' intensity...');

    try {
        // Load content if not already cached
        if (!resume.content) {
            await loadResumeContent(state.selectedId);
        }

        const data = await callApi('/polish-resume', { 
            resume_content: resume.content,
            intensity: currentPolishIntensity
        });
        
        const polished = data.polished_resume || '';
        currentTailoredContent = polished;
        currentFilename = resume.filename;

        // Display polished resume as text
        const pre = document.createElement('pre');
        pre.className = 'resume-text';
        pre.style.cssText = 'white-space: pre-wrap; word-wrap: break-word; font-size: 12px; line-height: 1.6; margin: 0;';
        pre.textContent = polished;
        polishedEl.innerHTML = '';
        polishedEl.appendChild(pre);

        // Show action buttons
        document.getElementById('polishActionButtons')?.setAttribute('style', 'display: flex;');

        // Display changes in the changes section
        if (data.changes) {
            displayPolishChanges(data.changes);
        }
    } catch (error) {
        showErrorInElement(state.tailoredPreviewElementId, `Error: ${error.message}`);
    }
}

/**
 * Display the changes report
 */
function displayPolishChanges(changes) {
    const changesSection = document.getElementById('polishChangesSection');
    const changesList = document.getElementById('polishChangesList');
    
    changesSection.style.display = 'block';
    
    const sectionIcons = {
        'Work Experience': '💼',
        'Education': '🎓',
        'Skills': '🔧',
        'Projects': '🚀',
        'Summary': '📝',
        'Certifications': '🏆',
        'Leadership': '👥',
        'Other': '📌'
    };
    
    function extractSection(change) {
        const match = change.match(/In\s+\[?([^\]]+)\]?:/);
        return match ? match[1] : null;
    }
    
    function getSectionIcon(section) {
        return sectionIcons[section] || '📋';
    }
    
    function formatChange(change) {
        const section = extractSection(change);
        if (!section) return change;
        
        // Remove "In [Section]:" prefix to get the actual change description
        const changeDesc = change.replace(/In\s+\[?[^\]]+\]?:\s*/, '').trim();
        
        // Check if change contains "Changed X -> Y" format
        const hasArrow = changeDesc.includes('->');
        
        return { section, changeDesc, hasArrow };
    }
    
    if (Array.isArray(changes) && changes.length > 0) {
        changesList.innerHTML = changes.map(change => {
            const parsed = formatChange(change);
            const icon = getSectionIcon(parsed.section);
            
            if (parsed.hasArrow) {
                // Format with before/after highlighting
                const parts = parsed.changeDesc.split('->');
                const before = parts[0].trim().replace(/^Changed\s+/, '').replace(/^['"]|['"]$/g, '');
                const after = parts[1]?.trim().replace(/^['"]|['"]$/g, '');
                
                return `<div style="display: flex; gap: 12px; align-items: flex-start; margin-bottom: 14px; padding: 12px; background: rgba(201, 168, 76, 0.08); border-radius: 8px; border-left: 4px solid var(--gold);">
                    <span style="font-size: 20px; flex-shrink: 0;">${icon}</span>
                    <div style="flex: 1; font-size: 13px;">
                        <div style="font-weight: 600; color: var(--gold); margin-bottom: 6px;">${parsed.section}</div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <span style="background: rgba(255, 0, 0, 0.1); padding: 4px 8px; border-radius: 4px; color: #ff6b6b; text-decoration: line-through; font-size: 12px;">${before}</span>
                            <span style="color: var(--text-muted);">→</span>
                            <span style="background: rgba(0, 255, 0, 0.1); padding: 4px 8px; border-radius: 4px; color: #51cf66; font-size: 12px;">${after}</span>
                        </div>
                    </div>
                </div>`;
            } else {
                // Simple format for non-before/after changes
                return `<div style="display: flex; gap: 12px; align-items: flex-start; margin-bottom: 14px; padding: 12px; background: rgba(201, 168, 76, 0.08); border-radius: 8px; border-left: 4px solid var(--gold);">
                    <span style="font-size: 20px; flex-shrink: 0;">${icon}</span>
                    <div style="flex: 1; font-size: 13px;">
                        <div style="font-weight: 600; color: var(--gold); margin-bottom: 4px;">${parsed.section}</div>
                        <div>${parsed.changeDesc}</div>
                    </div>
                </div>`;
            }
        }).join('');
    } else if (typeof changes === 'string') {
        changesList.innerHTML = `<div style="padding: 12px; font-size: 13px;">• ${changes}</div>`;
    } else {
        changesList.innerHTML = '<div style="padding: 12px; font-size: 13px; color: var(--text-dim);">Resume has been polished and optimized for maximum impact</div>';
    }
}

/**
 * Replace original resume with polished version
 */
async function replacePolishedResume() {
    console.log('[POLISH REPLACE] Starting replacePolishedResume');
    console.log('[POLISH REPLACE] currentTailoredContent exists:', !!currentTailoredContent);
    console.log('[POLISH REPLACE] currentFilename:', currentFilename);
    
    if (!currentTailoredContent || !currentFilename) {
        alert('No polished resume to replace');
        return;
    }

    if (!confirm('Replace the original resume with the polished version? This cannot be undone.')) {
        console.log('[POLISH REPLACE] User cancelled');
        return;
    }

    try {
        console.log('[POLISH REPLACE] Calling update-resume API');
        await callApi('/update-resume', {
            filename: currentFilename,
            content: currentTailoredContent
        });

        const resume = resumesData.find(r => r.filename === currentFilename);
        if (resume) {
            resume.content = currentTailoredContent;
            saveResumesToStorage();
        }

        alert('✓ Original resume replaced successfully!');
    } catch (error) {
        console.error('[POLISH REPLACE] Error:', error);
        alert('Error: ' + error.message);
    }
}

/**
 * Save polished resume with a new name
 */
async function savePolishedResumeAs() {
    console.log('[POLISH SAVE] Starting savePolishedResumeAs');
    console.log('[POLISH SAVE] currentTailoredContent exists:', !!currentTailoredContent);
    console.log('[POLISH SAVE] currentFilename:', currentFilename);
    
    if (!currentTailoredContent) {
        alert('No polished resume to save');
        return;
    }

    const originalName = currentFilename ? currentFilename.split('.')[0] : 'resume';
    const newName = await showInputModal('Save Polished Resume', `${originalName}_polished`);

    if (!newName?.trim()) {
        console.log('[POLISH SAVE] User cancelled or entered empty name');
        return;
    }

    console.log('[POLISH SAVE] Saving as:', newName);

    if (resumesData.some(r => r.filename.toLowerCase().startsWith(newName.toLowerCase()))) {
        const confirmed = await showConfirmModal('File Already Exists', 'A resume with this name exists. Overwrite?');
        if (!confirmed) {
            console.log('[POLISH SAVE] User cancelled overwrite');
            return;
        }
    }

    try {
        console.log('[POLISH SAVE] Calling saveResumeContent');
        const savedName = await saveResumeContent(null, currentTailoredContent, newName);
        console.log('[POLISH SAVE] File saved as:', savedName);
        
        await loadResumesFromFolder();
        console.log('[POLISH SAVE] Resumes reloaded');
        
        renderResumeListForMode(RESUME_MODES.POLISH);
        console.log('[POLISH SAVE] Resume list rendered');
        
        alert(`✓ Polished resume saved as "${savedName}"!`);
    } catch (error) {
        console.error('[POLISH SAVE] Error:', error);
        alert('Error: ' + error.message);
    }
}

/**
 * Show custom input modal dialog
 */
function showInputModal(title, defaultValue) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; align-items: center; justify-content: center; z-index: 10000;';
        
        const modal = document.createElement('div');
        modal.style.cssText = 'background: var(--dark-2); border: 2px solid var(--gold); border-radius: 12px; padding: 24px; min-width: 350px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);';
        
        const titleEl = document.createElement('div');
        titleEl.style.cssText = 'color: var(--gold); font-size: 14px; font-weight: 600; margin-bottom: 16px;';
        titleEl.textContent = title;
        modal.appendChild(titleEl);
        
        const input = document.createElement('input');
        input.type = 'text';
        input.value = defaultValue;
        input.style.cssText = 'width: 100%; padding: 10px; background: var(--dark-3); border: 1px solid var(--dark-4); color: var(--cream); border-radius: 6px; font-size: 13px; box-sizing: border-box; margin-bottom: 16px;';
        input.focus();
        input.select();
        modal.appendChild(input);
        
        const buttons = document.createElement('div');
        buttons.style.cssText = 'display: flex; gap: 10px;';
        
        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.cssText = 'flex: 1; padding: 10px; background: var(--dark-3); color: var(--text-muted); border: 1px solid var(--dark-4); border-radius: 6px; cursor: pointer; font-weight: 600;';
        cancelBtn.onclick = () => { overlay.remove(); resolve(null); };
        buttons.appendChild(cancelBtn);
        
        const okBtn = document.createElement('button');
        okBtn.textContent = 'Save';
        okBtn.style.cssText = 'flex: 1; padding: 10px; background: var(--gold); color: var(--dark); border: none; border-radius: 6px; cursor: pointer; font-weight: 600;';
        okBtn.onclick = () => { overlay.remove(); resolve(input.value); };
        buttons.appendChild(okBtn);
        
        input.onkeyup = (e) => { if (e.key === 'Enter') okBtn.click(); if (e.key === 'Escape') cancelBtn.click(); };
        
        modal.appendChild(buttons);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
    });
}

/**
 * Show confirmation modal
 */
function showConfirmModal(title, message) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.7); display: flex; align-items: center; justify-content: center; z-index: 10000;';
        
        const modal = document.createElement('div');
        modal.style.cssText = 'background: var(--dark-2); border: 2px solid var(--gold); border-radius: 12px; padding: 24px; min-width: 350px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);';
        
        const titleEl = document.createElement('div');
        titleEl.style.cssText = 'color: var(--gold); font-size: 14px; font-weight: 600; margin-bottom: 8px;';
        titleEl.textContent = title;
        modal.appendChild(titleEl);
        
        const msgEl = document.createElement('div');
        msgEl.style.cssText = 'color: var(--text-muted); font-size: 13px; line-height: 1.5; margin-bottom: 20px;';
        msgEl.textContent = message;
        modal.appendChild(msgEl);
        
        const buttons = document.createElement('div');
        buttons.style.cssText = 'display: flex; gap: 10px;';
        
        const noBtn = document.createElement('button');
        noBtn.textContent = 'No';
        noBtn.style.cssText = 'flex: 1; padding: 10px; background: var(--dark-3); color: var(--text-muted); border: 1px solid var(--dark-4); border-radius: 6px; cursor: pointer; font-weight: 600;';
        noBtn.onclick = () => { overlay.remove(); resolve(false); };
        buttons.appendChild(noBtn);
        
        const yesBtn = document.createElement('button');
        yesBtn.textContent = 'Yes';
        yesBtn.style.cssText = 'flex: 1; padding: 10px; background: var(--gold); color: var(--dark); border: none; border-radius: 6px; cursor: pointer; font-weight: 600;';
        yesBtn.onclick = () => { overlay.remove(); resolve(true); };
        buttons.appendChild(yesBtn);
        
        modal.appendChild(buttons);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
    });
}

async function tailorResume() {
    const state = resumeState[RESUME_MODES.TAILOR];
    const job = document.getElementById('jobInput')?.value || '';
    const position = document.getElementById('jobPosition')?.value || '';

    if (!job.trim()) {
        alert('Please enter a job description');
        return;
    }

    if (!currentFilename) {
        alert('Please select a resume first');
        return;
    }

    const tailoredEl = document.getElementById(state.tailoredPreviewElementId);
    tailoredEl.innerHTML = getPlaceholderHTML('Tailoring resume...');

    try {
        const data = await callApi('/tailor-resume', {
            filename: currentFilename,
            job_description: job,
            job_position: position
        });

        const tailored = data.tailored_resume || '';
        const pre = document.createElement('pre');
        pre.className = 'tailor-resume-text';
        pre.textContent = tailored;
        tailoredEl.innerHTML = '';
        tailoredEl.appendChild(pre);
        currentTailoredContent = tailored;

        document.getElementById('tailorActionButtons')?.setAttribute('style', 'display: flex');
    } catch (error) {
        showErrorInElement(state.tailoredPreviewElementId, `Error: ${error.message}`);
        document.getElementById('tailorActionButtons')?.setAttribute('style', 'display: none');
    }
}

async function replaceTailoredResume() {
    if (!currentTailoredContent || !currentFilename) {
        alert('No tailored resume to replace');
        return;
    }

    if (!confirm('Replace the original resume? This cannot be undone.')) return;

    try {
        await callApi('/update-resume', {
            filename: currentFilename,
            content: currentTailoredContent
        });

        const resume = resumesData.find(r => r.filename === currentFilename);
        if (resume) {
            resume.content = currentTailoredContent;
            saveResumesToStorage();
        }

        alert('✓ Original resume replaced successfully!');
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function saveTailoredResumeAs() {
    if (!currentTailoredContent) {
        alert('No tailored resume to save');
        return;
    }

    const originalName = currentFilename ? currentFilename.split('.')[0] : 'resume';
    const newName = await showInputModal('Save Tailored Resume', `${originalName}_tailored`);

    if (!newName?.trim()) return;

    if (resumesData.some(r => r.filename.toLowerCase().startsWith(newName.toLowerCase()))) {
        const confirmed = await showConfirmModal('File Already Exists', 'A resume with this name exists. Overwrite?');
        if (!confirmed) return;
    }

    try {
        const savedName = await saveResumeContent(null, currentTailoredContent, newName);
        await loadResumesFromFolder();
        renderResumeListForMode(RESUME_MODES.TAILOR);
        alert(`✓ Tailored resume saved as "${savedName}"!`);
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// ═══════════════════════════════════════════════════════════════
// LEGACY: RESUME UPLOAD & UTILITIES
// ═══════════════════════════════════════════════════════════════

async function handleResumeUpload() {
    const fileInput = document.getElementById('resumeFile');
    if (!fileInput?.files.length) return;

    const file = fileInput.files[0];
    if (!file.name.match(/\.(txt|pdf)$/i)) {
        alert('Please select a .txt or .pdf file');
        return;
    }

    try {
        const statusEl = document.getElementById('uploadStatus');
        showStatus('uploadStatus', '📤 Uploading resume...', 'loading');

        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/parse-resume`, {
            method: 'POST', body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Upload failed');

        await loadResumesFromFolder();
        renderResumeListForMode(RESUME_MODES.MAIN);

        showStatus('uploadStatus', '✓ Resume uploaded successfully!', 'success');
        hideStatus('uploadStatus', 3000);
        fileInput.value = '';
    } catch (error) {
        showStatus('uploadStatus', `✗ Upload failed: ${error.message}`, 'error');
    }
}

// Utilities
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ═══════════════════════════════════════════════════════════════
// FEEDBACK SECTION (PLACEHOLDER - NOT YET WIRED)
// ═══════════════════════════════════════════════════════════════

/**
 * Submit user feedback (placeholder - not yet connected to backend)
 */
function submitFeedback() {
    const feedbackType = document.getElementById('feedbackType')?.value;
    const feedbackMessage = document.getElementById('feedbackMessage')?.value;
    
    if (!feedbackMessage?.trim()) {
        alert('Please enter your feedback');
        return;
    }
    
    // TODO: Wire to backend feedback collection endpoint
    console.log('[FEEDBACK] Type:', feedbackType);
    console.log('[FEEDBACK] Message:', feedbackMessage);
    
    // Placeholder response
    alert('✓ Thank you for your feedback! This feature will be wired soon.');
    
    // Clear form
    document.getElementById('feedbackMessage').value = '';
}
