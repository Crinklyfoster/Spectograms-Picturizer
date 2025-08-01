// Motor Audio Analyzer - Frontend JavaScript

// Theme Management
function initTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeButton(theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    const themeButton = document.getElementById('theme-toggle');
    if (themeButton) {
        themeButton.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
}

// File Upload Handling
function initFileUpload() {
    const fileInput = document.getElementById('audio_file');
    const fileInfo = document.getElementById('file-info');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const uploadBtn = document.getElementById('upload-btn');

    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file) {
                // Update file info
                fileName.textContent = file.name;
                fileSize.textContent = formatFileSize(file.size);
                fileInfo.style.display = 'block';
                
                // Validate file
                const validTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/flac', 'audio/m4a'];
                const maxSize = 50 * 1024 * 1024; // 50MB
                
                if (!validTypes.some(type => file.type.includes(type.split('/')[1]))) {
                    showAlert('Invalid file type. Please select a WAV, MP3, FLAC, or M4A file.', 'error');
                    uploadBtn.disabled = true;
                    return;
                }
                
                if (file.size > maxSize) {
                    showAlert('File too large. Maximum size is 50MB.', 'error');
                    uploadBtn.disabled = true;
                    return;
                }
                
                // Enable upload button
                uploadBtn.disabled = false;
                
                // Update file label
                const fileLabel = document.querySelector('.file-label .file-text');
                if (fileLabel) {
                    fileLabel.textContent = 'File Selected ✓';
                }
                
            } else {
                fileInfo.style.display = 'none';
                uploadBtn.disabled = true;
            }
        });
    }
}

// Tab Management
function showTab(tabId) {
    // Hide all tab panes
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach(pane => pane.classList.remove('active'));
    
    // Remove active class from all buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    const selectedTab = document.getElementById(tabId);
    const selectedButton = document.querySelector(`[onclick="showTab('${tabId}')"]`);
    
    if (selectedTab) selectedTab.classList.add('active');
    if (selectedButton) selectedButton.classList.add('active');
}

// Feature Table Filtering
function toggleFeatureCategory(category) {
    const button = event.target;
    const isActive = button.classList.contains('active');
    
    if (isActive) {
        button.classList.remove('active');
        hideFeatureCategory(category);
    } else {
        button.classList.add('active');
        showFeatureCategory(category);
    }
}

function showFeatureCategory(category) {
    const rows = document.querySelectorAll(`[data-category="${category}"]`);
    rows.forEach(row => row.classList.remove('hidden'));
}

function hideFeatureCategory(category) {
    const rows = document.querySelectorAll(`[data-category="${category}"]`);
    rows.forEach(row => row.classList.add('hidden'));
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showAlert(message, type = 'info') {
    const alertsContainer = document.querySelector('.flash-messages');
    if (!alertsContainer) return;
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        ${message}
        <button class="alert-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

// Form Submission with Loading
function handleFormSubmission() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading">🔄 Processing...</span>';
            }
        });
    });
}

// Auto-hide Flash Messages
function autoHideFlashMessages() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentElement) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%)';
                setTimeout(() => alert.remove(), 300);
            }
        }, 5000);
    });
}

// Smooth Scrolling for Anchors
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            
            if (targetSection) {
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Keyboard Shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Alt + T: Toggle theme
        if (e.altKey && e.key === 't') {
            e.preventDefault();
            toggleTheme();
        }
        
        // Alt + U: Focus file upload
        if (e.altKey && e.key === 'u') {
            e.preventDefault();
            const fileInput = document.getElementById('audio_file');
            if (fileInput) fileInput.focus();
        }
        
        // Escape: Close modals/alerts
        if (e.key === 'Escape') {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => alert.remove());
        }
    });
}

// Image Loading Error Handling
function handleImageErrors() {
    const images = document.querySelectorAll('.spectrogram-image');
    
    images.forEach(img => {
        img.addEventListener('error', function() {
            this.parentElement.innerHTML = `
                <div class="error-message">
                    <p>❌ Failed to load spectrogram image</p>
                    <p class="error-detail">The image could not be displayed. Please try refreshing the page.</p>
                </div>
            `;
        });
    });
}

// Enhanced Audio Player Handling
function initAudioPlayer() {
    const audioPlayer = document.querySelector('.audio-player');
    
    if (audioPlayer) {
        // Handle audio loading errors
        audioPlayer.addEventListener('error', function(e) {
            console.error('Audio loading error:', e);
            showAudioError();
        });
        
        // Handle successful audio load
        audioPlayer.addEventListener('loadedmetadata', function() {
            console.log('Audio loaded successfully');
            const duration = this.duration;
            updateAudioInfo(duration);
        });
        
        // Handle audio load start
        audioPlayer.addEventListener('loadstart', function() {
            console.log('Audio loading started');
        });
        
        // Handle audio can play
        audioPlayer.addEventListener('canplay', function() {
            console.log('Audio can start playing');
        });
    }
}

function showAudioError() {
    const audioCard = document.querySelector('.audio-card');
    if (audioCard) {
        const errorMessage = document.createElement('div');
        errorMessage.className = 'audio-error';
        errorMessage.innerHTML = `
            <p>❌ Unable to play audio file</p>
            <p>This might be due to an unsupported format or file corruption.</p>
            <p>Try downloading the file directly using the button below.</p>
        `;
        
        // Insert error message after the audio player
        const audioPlayer = audioCard.querySelector('.audio-player');
        if (audioPlayer) {
            audioPlayer.parentNode.insertBefore(errorMessage, audioPlayer.nextSibling);
        }
    }
}

function updateAudioInfo(duration) {
    // Update duration display if needed
    const durationElements = document.querySelectorAll('.duration-display');
    durationElements.forEach(element => {
        element.textContent = formatDuration(duration);
    });
}

function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

// Initialize Everything
document.addEventListener('DOMContentLoaded', function() {
    initTheme();
    initFileUpload();
    handleFormSubmission();
    autoHideFlashMessages();
    initSmoothScrolling();
    initKeyboardShortcuts();
    handleImageErrors();
    initAudioPlayer();
    
    // Theme toggle button
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Initialize first tab as active if on results page
    const firstTabBtn = document.querySelector('.tab-btn');
    if (firstTabBtn && !document.querySelector('.tab-btn.active')) {
        firstTabBtn.click();
    }
    
    console.log('Motor Audio Analyzer initialized ✓');
});

// Export functions for global access
window.showTab = showTab;
window.toggleFeatureCategory = toggleFeatureCategory;
window.toggleTheme = toggleTheme;
