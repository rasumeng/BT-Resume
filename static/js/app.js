// ═══════════════════════════════════════════════════════════════
// GLOBAL VARIABLES
// ═══════════════════════════════════════════════════════════════

const API_BASE = 'http://localhost:5000/api';
let currentSessionId = null;
let currentFilename = null;

// Modern resumes management
let currentSelectedResume = null;
let resumesData = [];

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    loadSavedResumes();
    initResumesModern();
});

// ═══════════════════════════════════════════════════════════════
// UI HELPERS
// ═══════════════════════════════════════════════════════════════

function switchPanel(panelId, button) {
    // Hide all panels
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    // Show selected panel
    document.getElementById(panelId).classList.add('active');
    button.classList.add('active');

    // Update header title
    const titles = {
        'panel-my-resumes': 'RESUMES',
        'panel-bullet-polish': 'POLISH BULLETS',
        'panel-job-tailor': 'TAILOR RESUME',
        'panel-experience': 'EXPERIENCE'
    };
    document.getElementById('headerTitle').textContent = titles[panelId] || 'BEYOND THE RESUME';
    
    // Initialize modern resumes when switching to Resumes panel
    if (panelId === 'panel-my-resumes') {
        initResumesModern();
    }
}

function switchTab(tabId, button) {
    const container = button.closest('.tab-container').parentElement;
    container.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    container.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    button.classList.add('active');
}

function showStatus(elementId, message, type) {
    const el = document.getElementById(elementId);
    el.innerHTML = `<div class="status ${type}">${message}</div>`;
    el.style.display = 'block';
}

function hideStatus(elementId) {
    document.getElementById(elementId).style.display = 'none';
}

function showPreviewStatus(message, type) {
    const previewEl = document.getElementById('resumePreview');
    const statusClass = type === 'loading' ? '⏳' : type === 'success' ? '✓' : '✗';
    const color = type === 'success' ? 'var(--gold)' : type === 'error' ? '#FF6B6B' : 'var(--text-muted)';
    
    previewEl.innerHTML = `
        <div style="text-align: center; display: flex; flex-direction: column; gap: var(--spacing-lg); align-items: center;">
            <div style="font-size: 48px; font-weight: bold; color: ${color};">${statusClass}</div>
            <div style="font-size: 16px; color: var(--text-muted); max-width: 300px;">${message}</div>
        </div>
    `;
    
    document.getElementById('resumePreviewSection').style.display = 'block';
}

// ═══════════════════════════════════════════════════════════════
// PDF VIEWER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

let currentPdfDoc = null;
let currentPdfPage = 1;

/**
 * Render a PDF page using PDF.js
 */
async function renderPdfPage(pdfDoc, pageNum, canvas, ctx) {
    const page = await pdfDoc.getPage(pageNum);
    const viewport = page.getViewport({ scale: 1.5 });
    
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    
    const renderContext = {
        canvasContext: ctx,
        viewport: viewport
    };
    
    await page.render(renderContext).promise;
}

/**
 * Display PDF in preview container
 */
async function displayPdf(filename) {
    const previewContent = document.getElementById('resumePreview');
    
    try {
        // Show loading
        previewContent.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
                <div style="text-align: center; color: var(--text-muted);">
                    <div style="font-size: 24px; margin-bottom: 12px; animation: spin 2s linear infinite;">⏳</div>
                    <div>Loading PDF...</div>
                </div>
            </div>
        `;
        
        // Fetch PDF file
        const response = await fetch(`${API_BASE}/get-resume?filename=${encodeURIComponent(filename)}`);
        if (!response.ok) throw new Error('Failed to load PDF');
        
        const arrayBuffer = await response.arrayBuffer();
        
        // Load PDF with PDF.js
        const pdfDoc = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
        currentPdfDoc = pdfDoc;
        currentPdfPage = 1;
        
        // Create container for PDF viewer
        previewContent.innerHTML = `
            <div style="display: flex; flex-direction: column; height: 100%; gap: 10px;">
                <!-- PDF Navigation Bar -->
                <div style="display: flex; align-items: center; justify-content: space-between; padding: 10px; background: rgba(0,0,0,0.3); border-radius: 6px; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button id="pdfPrevBtn" style="padding: 6px 12px; background: var(--gold); color: var(--dark); border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">← Previous</button>
                        <input id="pdfPageNum" type="number" value="1" min="1" max="${pdfDoc.numPages}" style="width: 50px; padding: 6px; border: 1px solid var(--gold); background: var(--dark-3); color: var(--cream); border-radius: 4px; text-align: center;">
                        <span style="color: var(--text-muted); font-size: 14px;" id="pdfPageInfo">of ${pdfDoc.numPages}</span>
                        <button id="pdfNextBtn" style="padding: 6px 12px; background: var(--gold); color: var(--dark); border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Next →</button>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <button id="pdfZoomOut" style="padding: 6px 12px; background: rgba(201,168,76,0.5); color: var(--cream); border: 1px solid var(--gold); border-radius: 4px; cursor: pointer;">−</button>
                        <span id="pdfZoomLevel" style="color: var(--text-muted); font-size: 14px; min-width: 50px; text-align: center;">150%</span>
                        <button id="pdfZoomIn" style="padding: 6px 12px; background: rgba(201,168,76,0.5); color: var(--cream); border: 1px solid var(--gold); border-radius: 4px; cursor: pointer;">+</button>
                    </div>
                </div>
                <!-- PDF Canvas -->
                <div style="flex: 1; overflow-y: auto; display: flex; justify-content: center; background: rgba(0,0,0,0.5); border-radius: 6px; padding: 10px;">
                    <canvas id="pdfCanvas" style="max-width: 100%; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border-radius: 4px;"></canvas>
                </div>
            </div>
        `;
        
        // Set up event listeners
        document.getElementById('pdfPrevBtn').addEventListener('click', () => previousPdfPage());
        document.getElementById('pdfNextBtn').addEventListener('click', () => nextPdfPage());
        document.getElementById('pdfPageNum').addEventListener('change', (e) => goToPdfPage(parseInt(e.target.value)));
        document.getElementById('pdfZoomIn').addEventListener('click', () => zoomPdfIn());
        document.getElementById('pdfZoomOut').addEventListener('click', () => zoomPdfOut());
        
        // Render first page
        const canvas = document.getElementById('pdfCanvas');
        const ctx = canvas.getContext('2d');
        await renderPdfPage(pdfDoc, currentPdfPage, canvas, ctx);
        
    } catch (error) {
        previewContent.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #e74c3c;">
                <div style="text-align: center;">
                    <div style="font-size: 36px; margin-bottom: 12px;">❌</div>
                    <div>Failed to load PDF</div>
                    <div style="font-size: 12px; color: var(--text-dim); margin-top: 8px;">${error.message}</div>
                </div>
            </div>
        `;
        console.error('Error displaying PDF:', error);
    }
}

/**
 * Navigate PDF pages
 */
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
    const ctx = canvas.getContext('2d');
    const pageInput = document.getElementById('pdfPageNum');
    
    await renderPdfPage(currentPdfDoc, currentPdfPage, canvas, ctx);
    pageInput.value = currentPdfPage;
}

let currentPdfScale = 1.5;

async function zoomPdfIn() {
    currentPdfScale += 0.25;
    updatePdfZoom();
}

async function zoomPdfOut() {
    if (currentPdfScale > 0.5) {
        currentPdfScale -= 0.25;
        updatePdfZoom();
    }
}

async function updatePdfZoom() {
    const canvas = document.getElementById('pdfCanvas');
    const ctx = canvas.getContext('2d');
    const page = await currentPdfDoc.getPage(currentPdfPage);
    const viewport = page.getViewport({ scale: currentPdfScale });
    
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    
    const renderContext = {
        canvasContext: ctx,
        viewport: viewport
    };
    
    await page.render(renderContext).promise;
    document.getElementById('pdfZoomLevel').textContent = Math.round(currentPdfScale * 66.67) + '%';
}

// ═══════════════════════════════════════════════════════════════
// MODERN RESUMES MANAGEMENT - LOCAL STORAGE & UI
// ═══════════════════════════════════════════════════════════════

/**
 * Initialize the modern resumes interface
 */
function initResumesModern() {
    loadResumesFromStorage();
    renderResumeList();
}

/**
 * Handle resume file upload - Just add to list, don't read content yet
 */
function handleResumeUpload() {
    const fileInput = document.getElementById('resumeFile');
    if (!fileInput.files.length) {
        return;
    }

    const file = fileInput.files[0];
    
    // Check file type
    if (!file.name.endsWith('.txt') && !file.name.endsWith('.pdf')) {
        alert('Please select a .txt or .pdf file');
        return;
    }

    // Create resume object WITHOUT reading content yet
    const resume = {
        id: Date.now(),
        name: file.name,
        file: file,  // Store the actual File object
        content: null,  // Will be loaded when preview is clicked
        uploadDate: new Date().toLocaleDateString(),
        scores: null,
        isGrading: false
    };

    // Add to data and storage
    resumesData.push(resume);
    saveResumesToStorage();
    
    console.log('Resume added to list:', file.name);
    
    // Update UI
    renderResumeList();
    
    // Reset file input
    fileInput.value = '';
}

/**
 * Load content from file (called when preview is clicked)
 */
function loadResumeContent(resumeId) {
    const resume = resumesData.find(r => r.id === resumeId);
    if (!resume) {
        return Promise.reject(new Error('Resume not found'));
    }

    // If content already loaded, no need to read again
    if (resume.content) {
        return Promise.resolve();
    }

    // If File object is available, read from it
    if (resume.file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();

            reader.onload = function(e) {
                try {
                    const fileContent = e.target.result;
                    
                    if (!fileContent || fileContent.trim().length === 0) {
                        throw new Error('File is empty');
                    }

                    resume.content = fileContent;
                    saveResumesToStorage();
                    console.log('Content loaded from file:', resume.name);
                    resolve();
                } catch (error) {
                    console.error('Error loading content:', error);
                    reject(error);
                }
            };

            reader.onerror = function(error) {
                console.error('FileReader error:', error);
                reject(new Error('Failed to read file'));
            };

            reader.readAsText(resume.file);
        });
    }

    // If no file object (e.g., page reloaded), show message
    return Promise.reject(new Error('File reference lost after reload. Please re-add the resume.'));
}

/**
 * Load resumes from localStorage
 */
function loadResumesFromStorage() {
    const stored = localStorage.getItem('resumesData');
    if (stored) {
        try {
            resumesData = JSON.parse(stored);
            // Note: File objects can't be serialized, so they'll be null after loading from storage
            // Content will be reloaded from file when needed
        } catch (error) {
            console.error('Error loading from localStorage:', error);
            resumesData = [];
        }
    }
}

/**
 * Save resumes to localStorage (only serializable data)
 */
function saveResumesToStorage() {
    // Only save data that can be serialized (not File objects)
    const dataToSave = resumesData.map(r => ({
        id: r.id,
        name: r.name,
        content: r.content,  // Will be null if not previewed yet
        uploadDate: r.uploadDate,
        scores: r.scores,
        isGrading: r.isGrading
    }));
    localStorage.setItem('resumesData', JSON.stringify(dataToSave));
}

/**
 * Render the resume list
 */
function renderResumeList() {
    const resumeListContainer = document.getElementById('resumeList');

    if (resumesData.length === 0) {
        resumeListContainer.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <div>No resumes yet</div>
                <div style="font-size: 11px; margin-top: 4px;">Click "+ Add Resume" to get started</div>
            </div>
        `;
        return;
    }

    resumeListContainer.innerHTML = resumesData.map(resume => `
        <div class="resume-card ${currentSelectedResume === resume.id ? 'active' : ''}" onclick="selectResume(${resume.id})">
            <div class="resume-card-title">${resume.name}</div>
            <div class="resume-card-meta">
                <span>${resume.uploadDate}</span>
                <span>${resume.scores ? '✓ Graded' : (resume.content ? '•' : '○')}</span>
            </div>
        </div>
    `).join('');
}

/**
 * Select and display a resume
 */
function selectResume(resumeId) {
    currentSelectedResume = resumeId;
    const resume = resumesData.find(r => r.id === resumeId);

    if (!resume) return;

    // Update active state
    renderResumeList();

    // Detect file type from filename
    const fileExt = resume.name.split('.').pop().toLowerCase();
    
    // Show loading state
    const previewContent = document.getElementById('resumePreview');
    previewContent.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
            <div style="text-align: center; color: var(--text-muted);">
                <div style="font-size: 24px; margin-bottom: 12px; animation: spin 2s linear infinite;">⏳</div>
                <div>Loading resume...</div>
            </div>
        </div>
    `;

    // Display preview based on file type
    if (fileExt === 'pdf') {
        // For PDFs, use PDF.js viewer
        displayPdf(resume.name)
            .then(() => {
                // Show action buttons
                document.getElementById('actionButtons').style.display = 'flex';

                // Update grading panel
                updateGradingPanel(resume);
            })
            .catch(error => {
                previewContent.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #e74c3c;">
                        <div style="text-align: center;">
                            <div style="font-size: 36px; margin-bottom: 12px;">❌</div>
                            <div>Failed to load PDF</div>
                            <div style="font-size: 12px; color: var(--text-dim); margin-top: 8px;">${error.message}</div>
                        </div>
                    </div>
                `;
            });
    } else {
        // For TXT files, use text display
        loadResumeContent(resumeId)
            .then(() => {
                // Display preview using pre tag to preserve formatting
                const resume = resumesData.find(r => r.id === resumeId);
                const preElement = document.createElement('pre');
                preElement.className = 'resume-text';
                preElement.setAttribute('style', 'white-space: pre-wrap; word-wrap: break-word; font-size: 12px; line-height: 1.6; margin: 0;');
                preElement.textContent = resume.content;  // Using textContent to avoid HTML interpretation
                previewContent.innerHTML = '';  // Clear loading state
                previewContent.appendChild(preElement);
                
                // Show action buttons
                document.getElementById('actionButtons').style.display = 'flex';

                // Update grading panel
                updateGradingPanel(resume);
            })
            .catch(error => {
                previewContent.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #e74c3c;">
                        <div style="text-align: center;">
                            <div style="font-size: 36px; margin-bottom: 12px;">❌</div>
                            <div>Failed to load resume</div>
                            <div style="font-size: 12px; color: var(--text-dim); margin-top: 8px;">${error.message}</div>
                        </div>
                    </div>
                `;
            });
    }
}


/**
 * Update the grading panel with resume scores
 */
function updateGradingPanel(resume) {
    const gradingContent = document.getElementById('gradingContent');

    if (!resume.scores) {
        gradingContent.innerHTML = `
            <div class="grading-empty">
                <div class="grading-empty-icon">📊</div>
                <div>No scores yet</div>
                <div style="font-size: 11px; margin-top: 4px;">Grade this resume to see results</div>
            </div>
        `;
        return;
    }

    const scores = resume.scores;
    const getScoreClass = (score) => {
        if (score >= 75) return 'high';
        if (score >= 50) return 'medium';
        return 'low';
    };

    gradingContent.innerHTML = `
        <div class="score-section">
            <h4>📈 Overall Metrics</h4>
            <div class="score-grid">
                <div class="score-item">
                    <div class="score-item-label">Overall Score</div>
                    <div class="score-item-value ${getScoreClass(scores.overall)}">${scores.overall}</div>
                </div>
                <div class="score-item">
                    <div class="score-item-label">ATS Compatibility</div>
                    <div class="score-item-value ${getScoreClass(scores.ats)}">${scores.ats}</div>
                </div>
            </div>
        </div>

        <div class="score-section">
            <h4>🔍 Detailed Breakdown</h4>
            <div class="score-grid">
                <div class="score-item">
                    <div class="score-item-label">Sections Quality</div>
                    <div class="score-item-value ${getScoreClass(scores.sections)}">${scores.sections}</div>
                </div>
                <div class="score-item">
                    <div class="score-item-label">Bullet Points</div>
                    <div class="score-item-value ${getScoreClass(scores.bullets)}">${scores.bullets}</div>
                </div>
            </div>
        </div>

        ${scores.feedback ? `
            <div class="score-section">
                <h4>💡 Feedback</h4>
                <div style="background: var(--dark-3); padding: 12px; border-radius: 6px; border-left: 3px solid var(--gold); font-size: 12px; line-height: 1.6; color: var(--text-muted);">
                    ${scores.feedback}
                </div>
            </div>
        ` : ''}
    `;
}

/**
 * Grade the selected resume (triggers API call)
 */
function gradeSelectedResume() {
    if (!currentSelectedResume) {
        alert('Please select a resume first');
        return;
    }

    const resume = resumesData.find(r => r.id === currentSelectedResume);
    if (!resume) return;

    // Prevent multiple simultaneous grading requests
    if (resume.isGrading) {
        return;
    }

    resume.isGrading = true;

    // Show loading state
    const gradingContent = document.getElementById('gradingContent');
    gradingContent.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
            <div style="text-align: center;">
                <div style="font-size: 32px; margin-bottom: 12px; animation: spin 2s linear infinite;">⚙️</div>
                <div style="color: var(--text-muted);">Analyzing resume...</div>
                <div style="font-size: 12px; color: var(--text-dim); margin-top: 8px;">Sending to AI grader</div>
            </div>
        </div>
        <style>
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        </style>
    `;

    // Call backend API to grade the resume
    fetch(`${API_BASE}/grade-resume`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            resume_text: resume.content
        })
    })
    .then(response => response.json())
    .then(data => {
        resume.isGrading = false;

        if (data.error) {
            throw new Error(data.error);
        }

        // Store scores from API response
        resume.scores = {
            overall: Math.round(data.scores.overall),
            ats: Math.round(data.scores.ats_score),
            sections: Math.round(data.scores.sections_score),
            bullets: Math.round(data.scores.bullets_score),
            feedback: `Keywords: ${data.scores.keywords_score}/100 - ${data.scores.feedback || 'Resume analyzed by AI'}`
        };

        saveResumesToStorage();
        updateGradingPanel(resume);
        renderResumeList();
    })
    .catch(error => {
        resume.isGrading = false;
        console.error('Grading error:', error);
        
        gradingContent.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; height: 100%; flex-direction: column; color: #e74c3c;">
                <div style="font-size: 36px; margin-bottom: 12px;">❌</div>
                <div>Failed to grade resume</div>
                <div style="font-size: 12px; color: var(--text-dim); margin-top: 8px;">${error.message}</div>
                <button class="btn-grade" onclick="gradeSelectedResume()" style="margin-top: 16px;">Retry</button>
            </div>
        `;
    });
}

/**
 * Download resume as PDF
 */
function downloadResumePDF() {
    if (!currentSelectedResume) {
        alert('Please select a resume first');
        return;
    }

    const resume = resumesData.find(r => r.id === currentSelectedResume);
    if (!resume) return;

    // Create a simple text download for now
    const element = document.createElement('a');
    const file = new Blob([resume.content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = resume.name.replace(/\.[^/.]+$/, '') + '_graded.txt';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// ═══════════════════════════════════════════════════════════════
// LEGACY RESUME MANAGEMENT - SAVED RESUMES
// ═══════════════════════════════════════════════════════════════

async function loadSavedResumes() {
    try {
        const response = await fetch(`${API_BASE}/list-resumes`, {
            method: 'GET'
        });

        const data = await response.json();

        if (response.ok && data.resumes.length > 0) {
            const listEl = document.getElementById('savedResumesList');
            const emptyEl = document.getElementById('savedResumesEmpty');
            
            listEl.innerHTML = '';
            
            data.resumes.forEach(resume => {
                const btn = document.createElement('button');
                btn.className = 'nav-btn';
                btn.style.width = '100%';
                btn.style.textAlign = 'left';
                btn.style.borderLeft = '3px solid transparent';
                btn.style.padding = 'var(--spacing-md) var(--spacing-sm)';
                btn.style.marginBottom = '0';
                btn.innerHTML = `📄 ${resume.name}`;
                btn.onclick = () => {
                    document.querySelectorAll('#savedResumesList .nav-btn').forEach(b => {
                        b.classList.remove('active');
                        b.style.borderLeftColor = 'transparent';
                        b.style.color = 'var(--text-muted)';
                    });
                    btn.classList.add('active');
                    btn.style.borderLeftColor = 'var(--gold)';
                    btn.style.color = 'var(--gold)';
                    loadResume(resume.name);
                };
                listEl.appendChild(btn);
            });
            
            emptyEl.style.display = 'none';
        } else {
            document.getElementById('savedResumesList').innerHTML = '';
            document.getElementById('savedResumesEmpty').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading saved resumes:', error);
    }
}

async function importResume() {
    const file = document.getElementById('resumeImportInput').files[0];
    if (!file) return;

    showPreviewStatus('Importing resume...', 'loading');
    document.getElementById('resumeScoresDisplay').style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Step 1: Save file
        const response = await fetch(`${API_BASE}/parse-resume`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            currentFilename = data.filename;
            
            // Step 2: Load preview (displays directly)
            await loadResumePreview(currentFilename);
            
            // Step 3: Reload saved resumes list
            loadSavedResumes();
        } else {
            showPreviewStatus(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showPreviewStatus(`Error: ${error.message}`, 'error');
    }
    
    // Reset file input
    document.getElementById('resumeImportInput').value = '';
}

async function loadResume(filename) {
    showPreviewStatus('Loading resume...', 'loading');
    document.getElementById('resumeScoresDisplay').style.display = 'none';

    try {
        currentFilename = filename;
        await loadResumePreview(filename);
    } catch (error) {
        showPreviewStatus(`Error: ${error.message}`, 'error');
    }
}

async function loadResumePreview(filename) {
    try {
        const response = await fetch(`${API_BASE}/preview-resume?filename=${encodeURIComponent(filename)}`);
        const data = await response.json();

        if (response.ok) {
            displayResumePreview(data.preview_type, data.preview_data);
        } else {
            throw new Error(data.error || 'Failed to load preview');
        }
    } catch (error) {
        console.error('Error loading preview:', error);
        throw error;
    }
}

function displayResumePreview(type, data) {
    const previewEl = document.getElementById('resumePreview');
    
    if (type === 'image') {
        previewEl.innerHTML = `<img src="${data}" style="max-width: 100%; height: auto; border-radius: var(--border-radius); box-shadow: 0 2px 8px rgba(0,0,0,0.2);" />`;
    } else {
        previewEl.innerHTML = `<pre style="background: var(--bg-secondary); padding: var(--spacing-md); border-radius: var(--border-radius); font-size: 12px; white-space: pre-wrap; word-wrap: break-word;">${data}</pre>`;
    }
    
    document.getElementById('resumePreviewSection').style.display = 'block';
    document.getElementById('resumeScoresDisplay').style.display = 'none';
}

// ═══════════════════════════════════════════════════════════════
// API CALLS - OTHER ENDPOINTS
// ═══════════════════════════════════════════════════════════════

async function gradeResume() {
    if (!currentFilename) {
        showPreviewStatus('Please load a resume first', 'error');
        return;
    }

    showPreviewStatus('Grading resume...', 'loading');

    try {
        const response = await fetch(`${API_BASE}/grade-resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: currentFilename })
        });

        const data = await response.json();

        if (response.ok) {
            const scores = data.scores;
            document.getElementById('scoreOverall').textContent = scores.overall || '-';
            document.getElementById('scoreATS').textContent = scores.ats_score || '-';
            document.getElementById('scoreSections').textContent = scores.sections_score || '-';
            document.getElementById('scoreBullets').textContent = scores.bullets_score || '-';

            document.getElementById('resumeScoresDisplay').style.display = 'block';
        } else {
            showPreviewStatus(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showPreviewStatus(`Error: ${error.message}`, 'error');
    }
}

async function polishBullets() {
    const text = document.getElementById('bulletsInput').value;
    if (!text.trim()) {
        showStatus('bulletStatus', 'Please enter bullets', 'error');
        return;
    }

    const bullets = text.split('\n').filter(b => b.trim());

    showStatus('bulletStatus', 'Polishing bullets...', 'loading');
    document.getElementById('bulletResults').style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/polish-bullets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bullets })
        });

        const data = await response.json();

        if (response.ok) {
            const list = document.getElementById('polishedBulletsList');
            list.innerHTML = data.polished_bullets.map(b =>
                `<div class="bullet-item">• ${b}</div>`
            ).join('');

            document.getElementById('bulletResults').style.display = 'block';
            showStatus('bulletStatus', '✓ Bullets polished!', 'success');
            setTimeout(() => hideStatus('bulletStatus'), 3000);
        } else {
            showStatus('bulletStatus', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('bulletStatus', `Error: ${error.message}`, 'error');
    }
}

async function tailorResume() {
    const job = document.getElementById('jobInput').value;
    if (!job.trim()) {
        showStatus('tailorStatus', 'Please enter a job description', 'error');
        return;
    }

    if (!currentFilename) {
        showStatus('tailorStatus', 'Please load a resume first', 'error');
        return;
    }

    showStatus('tailorStatus', 'Tailoring resume...', 'loading');

    try {
        const response = await fetch(`${API_BASE}/tailor-resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentFilename,
                job_description: job
            })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('tailorOutput').innerHTML = `<pre>${JSON.stringify(data.tailored_resume, null, 2)}</pre>`;
            document.getElementById('tailorResults').style.display = 'block';
            showStatus('tailorStatus', '✓ Resume tailored!', 'success');
            setTimeout(() => hideStatus('tailorStatus'), 3000);
        } else {
            showStatus('tailorStatus', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('tailorStatus', `Error: ${error.message}`, 'error');
    }
}

async function downloadPDF() {
    if (!currentFilename) {
        alert('No resume to download');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/generate-pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: currentFilename })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentFilename ? currentFilename.replace(/\.(pdf|txt)$/i, '.pdf') : 'resume.pdf';
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Failed to download PDF');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function generateExperience() {
    const text = document.getElementById('experienceInput').value;
    if (!text.trim()) {
        showStatus('experienceStatus', 'Please describe your experience', 'error');
        return;
    }

    showStatus('experienceStatus', 'Generating bullets...', 'loading');
    document.getElementById('experienceResults').style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/update-experience`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: text })
        });

        const data = await response.json();

        if (response.ok) {
            const bullets = data.bullets.split('\n').filter(b => b.trim());
            const list = document.getElementById('generatedBulletsList');
            list.innerHTML = bullets.map(b =>
                `<div class="bullet-item">• ${b.replace(/^- /, '').trim()}</div>`
            ).join('');

            document.getElementById('experienceResults').style.display = 'flex';
            showStatus('experienceStatus', '✓ Bullets generated!', 'success');
            setTimeout(() => hideStatus('experienceStatus'), 3000);
        } else {
            showStatus('experienceStatus', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('experienceStatus', `Error: ${error.message}`, 'error');
    }
}

// ═══════════════════════════════════════════════════════════════
// UTILITY HELPERS
// ═══════════════════════════════════════════════════════════════

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function switchTab(tabId, button) {
    const container = button.closest('.tab-container').parentElement;
    container.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    container.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    button.classList.add('active');
}

function showStatus(elementId, message, type) {
    const el = document.getElementById(elementId);
    el.innerHTML = `<div class="status ${type}">${message}</div>`;
    el.style.display = 'block';
}

function hideStatus(elementId) {
    document.getElementById(elementId).style.display = 'none';
}

function showPreviewStatus(message, type) {
    const previewEl = document.getElementById('resumePreview');
    const statusClass = type === 'loading' ? '⏳' : type === 'success' ? '✓' : '✗';
    const color = type === 'success' ? 'var(--gold)' : type === 'error' ? '#FF6B6B' : 'var(--text-muted)';
    
    previewEl.innerHTML = `
        <div style="text-align: center; display: flex; flex-direction: column; gap: var(--spacing-lg); align-items: center;">
            <div style="font-size: 48px; font-weight: bold; color: ${color};">${statusClass}</div>
            <div style="font-size: 16px; color: var(--text-muted); max-width: 300px;">${message}</div>
        </div>
    `;
    
    document.getElementById('resumePreviewSection').style.display = 'block';
}

// ═══════════════════════════════════════════════════════════════
// RESUME MANAGEMENT - NEW FUNCTIONS
// ═══════════════════════════════════════════════════════════════

async function loadSavedResumes() {
    try {
        const response = await fetch(`${API_BASE}/list-resumes`, {
            method: 'GET'
        });

        const data = await response.json();

        if (response.ok && data.resumes.length > 0) {
            const listEl = document.getElementById('savedResumesList');
            const emptyEl = document.getElementById('savedResumesEmpty');
            
            listEl.innerHTML = '';
            
            data.resumes.forEach(resume => {
                const btn = document.createElement('button');
                btn.className = 'nav-btn';
                btn.style.width = '100%';
                btn.style.textAlign = 'left';
                btn.style.borderLeft = '3px solid transparent';
                btn.style.padding = 'var(--spacing-md) var(--spacing-sm)';
                btn.style.marginBottom = '0';
                btn.innerHTML = `📄 ${resume.name}`;
                btn.onclick = () => {
                    document.querySelectorAll('#savedResumesList .nav-btn').forEach(b => {
                        b.classList.remove('active');
                        b.style.borderLeftColor = 'transparent';
                        b.style.color = 'var(--text-muted)';
                    });
                    btn.classList.add('active');
                    btn.style.borderLeftColor = 'var(--gold)';
                    btn.style.color = 'var(--gold)';
                    loadResume(resume.name);
                };
                listEl.appendChild(btn);
            });
            
            emptyEl.style.display = 'none';
        } else {
            document.getElementById('savedResumesList').innerHTML = '';
            document.getElementById('savedResumesEmpty').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading saved resumes:', error);
    }
}

async function importResume() {
    const file = document.getElementById('resumeImportInput').files[0];
    if (!file) return;

    showPreviewStatus('Importing resume...', 'loading');
    document.getElementById('resumeScoresDisplay').style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        // Step 1: Save file
        const response = await fetch(`${API_BASE}/parse-resume`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            currentFilename = data.filename;
            
            // Step 2: Load preview (displays directly)
            await loadResumePreview(currentFilename);
            
            // Step 3: Reload saved resumes list
            loadSavedResumes();
        } else {
            showPreviewStatus(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showPreviewStatus(`Error: ${error.message}`, 'error');
    }
    
    // Reset file input
    document.getElementById('resumeImportInput').value = '';
}

async function loadResume(filename) {
    showPreviewStatus('Loading resume...', 'loading');
    document.getElementById('resumeScoresDisplay').style.display = 'none';

    try {
        currentFilename = filename;
        await loadResumePreview(filename);
    } catch (error) {
        showPreviewStatus(`Error: ${error.message}`, 'error');
    }
}

async function loadResumePreview(filename) {
    try {
        const response = await fetch(`${API_BASE}/preview-resume?filename=${encodeURIComponent(filename)}`);
        const data = await response.json();

        if (response.ok) {
            displayResumePreview(data.preview_type, data.preview_data);
        } else {
            throw new Error(data.error || 'Failed to load preview');
        }
    } catch (error) {
        console.error('Error loading preview:', error);
        throw error;
    }
}

function displayResumePreview(type, data) {
    const previewEl = document.getElementById('resumePreview');
    
    if (type === 'image') {
        // Display PDF image - let container handle scrolling
        previewEl.innerHTML = `<img src="${data}" style="max-width: 100%; height: auto; border-radius: var(--border-radius); box-shadow: 0 2px 8px rgba(0,0,0,0.2);" />`;
    } else {
        // Display text - let container handle scrolling
        previewEl.innerHTML = `<pre style="background: var(--bg-secondary); padding: var(--spacing-md); border-radius: var(--border-radius); font-size: 12px; white-space: pre-wrap; word-wrap: break-word;">${data}</pre>`;
    }
    
    document.getElementById('resumePreviewSection').style.display = 'block';
    
    // Hide scores until graded
    document.getElementById('resumeScoresDisplay').style.display = 'none';
}

// ═══════════════════════════════════════════════════════════════
// API CALLS - EXISTING & UPDATED
// ═══════════════════════════════════════════════════════════════

async function gradeResume() {
    if (!currentFilename) {
        showPreviewStatus('Please load a resume first', 'error');
        return;
    }

    showPreviewStatus('Grading resume...', 'loading');

    try {
        const response = await fetch(`${API_BASE}/grade-resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: currentFilename })
        });

        const data = await response.json();

        if (response.ok) {
            const scores = data.scores;
            document.getElementById('scoreOverall').textContent = scores.overall || '-';
            document.getElementById('scoreATS').textContent = scores.ats_score || '-';
            document.getElementById('scoreSections').textContent = scores.sections_score || '-';
            document.getElementById('scoreBullets').textContent = scores.bullets_score || '-';

            document.getElementById('resumeScoresDisplay').style.display = 'block';
        } else {
            showPreviewStatus(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showPreviewStatus(`Error: ${error.message}`, 'error');
    }
}

async function polishBullets() {
    const text = document.getElementById('bulletsInput').value;
    if (!text.trim()) {
        showStatus('bulletStatus', 'Please enter bullets', 'error');
        return;
    }

    const bullets = text.split('\n').filter(b => b.trim());

    showStatus('bulletStatus', 'Polishing bullets...', 'loading');
    document.getElementById('bulletResults').style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/polish-bullets`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bullets })
        });

        const data = await response.json();

        if (response.ok) {
            const list = document.getElementById('polishedBulletsList');
            list.innerHTML = data.polished_bullets.map(b =>
                `<div class="bullet-item">• ${b}</div>`
            ).join('');

            document.getElementById('bulletResults').style.display = 'block';
            showStatus('bulletStatus', '✓ Bullets polished!', 'success');
            setTimeout(() => hideStatus('bulletStatus'), 3000);
        } else {
            showStatus('bulletStatus', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('bulletStatus', `Error: ${error.message}`, 'error');
    }
}

async function tailorResume() {
    const job = document.getElementById('jobInput').value;
    if (!job.trim()) {
        showStatus('tailorStatus', 'Please enter a job description', 'error');
        return;
    }

    if (!currentFilename) {
        showStatus('tailorStatus', 'Please load a resume first', 'error');
        return;
    }

    showStatus('tailorStatus', 'Tailoring resume...', 'loading');

    try {
        const response = await fetch(`${API_BASE}/tailor-resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentFilename,
                job_description: job
            })
        });

        const data = await response.json();

        if (response.ok) {
            document.getElementById('tailorOutput').innerHTML = `<pre>${JSON.stringify(data.tailored_resume, null, 2)}</pre>`;
            document.getElementById('tailorResults').style.display = 'block';
            showStatus('tailorStatus', '✓ Resume tailored!', 'success');
            setTimeout(() => hideStatus('tailorStatus'), 3000);
        } else {
            showStatus('tailorStatus', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('tailorStatus', `Error: ${error.message}`, 'error');
    }
}

async function downloadPDF() {
    if (!currentFilename) {
        alert('No resume to download');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/generate-pdf`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: currentFilename })
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = currentFilename ? currentFilename.replace(/\.(pdf|txt)$/i, '.pdf') : 'resume.pdf';
            a.click();
            window.URL.revokeObjectURL(url);
        } else {
            alert('Failed to download PDF');
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

async function generateExperience() {
    const text = document.getElementById('experienceInput').value;
    if (!text.trim()) {
        showStatus('experienceStatus', 'Please describe your experience', 'error');
        return;
    }

    showStatus('experienceStatus', 'Generating bullets...', 'loading');
    document.getElementById('experienceResults').style.display = 'none';

    try {
        const response = await fetch(`${API_BASE}/update-experience`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: text })
        });

        const data = await response.json();

        if (response.ok) {
            const bullets = data.bullets.split('\n').filter(b => b.trim());
            const list = document.getElementById('generatedBulletsList');
            list.innerHTML = bullets.map(b =>
                `<div class="bullet-item">• ${b.replace(/^- /, '').trim()}</div>`
            ).join('');

            document.getElementById('experienceResults').style.display = 'flex';
            showStatus('experienceStatus', '✓ Bullets generated!', 'success');
            setTimeout(() => hideStatus('experienceStatus'), 3000);
        } else {
            showStatus('experienceStatus', `Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showStatus('experienceStatus', `Error: ${error.message}`, 'error');
    }
}
