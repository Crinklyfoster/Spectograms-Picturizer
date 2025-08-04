// Motor Fault Detection App JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Initialize dark mode
    initializeDarkMode();
    
    // Initialize file upload handling
    initializeFileUpload();
    
    // Initialize clear functionality
    initializeClearButton();
    
    // Initialize download buttons
    initializeDownloadButtons();
}

// Dark Mode Toggle Functionality
function initializeDarkMode() {
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // Add click event listener
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = body.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            setTheme(newTheme);
        });
    }
}

function setTheme(theme) {
    const body = document.body;
    const themeToggle = document.getElementById('theme-toggle');
    
    body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    if (themeToggle) {
        themeToggle.textContent = theme === 'light' ? '🌙 Dark Mode' : '☀️ Light Mode';
    }
}

// File Upload Handling
function initializeFileUpload() {
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');
    const uploadForm = document.getElementById('upload-form');
    
    if (fileInput && fileInfo) {
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            
            if (file) {
                // Display file information
                const fileSize = formatFileSize(file.size);
                const fileName = file.name;
                
                fileInfo.innerHTML = `
                    <strong>Selected file:</strong> ${fileName}<br>
                    <strong>Size:</strong> ${fileSize}
                `;
                fileInfo.style.display = 'block';
                
                // Validate file type
                const allowedTypes = ['audio/wav', 'audio/mpeg', 'audio/flac', 'audio/mp4', 'audio/ogg'];
                const fileExtension = fileName.split('.').pop().toLowerCase();
                const allowedExtensions = ['wav', 'mp3', 'flac', 'm4a', 'ogg'];
                
                if (!allowedExtensions.includes(fileExtension)) {
                    showAlert('Please select a valid audio file (WAV, MP3, FLAC, M4A, or OGG).', 'danger');
                    fileInput.value = '';
                    fileInfo.style.display = 'none';
                    return;
                }
                
                // Auto-submit form after file selection
                if (uploadForm) {
                    showLoading();
                    setTimeout(() => {
                        uploadForm.submit();
                    }, 500);
                }
            } else {
                fileInfo.style.display = 'none';
            }
        });
    }
}

// Clear Button Functionality
function initializeClearButton() {
    const clearButton = document.getElementById('clear-btn');
    
    if (clearButton) {
        clearButton.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to clear all results? This action cannot be undone.')) {
                event.preventDefault();
                return false;
            }
            
            showLoading();
        });
    }
}

// Download Button Functionality
function initializeDownloadButtons() {
    const downloadButtons = document.querySelectorAll('.download-btn');
    
    downloadButtons.forEach(button => {
        button.addEventListener('click', function() {
            const format = this.getAttribute('data-format');
            showAlert(`Downloading features as ${format.toUpperCase()}...`, 'info');
            
            // Add slight delay to show the message
            setTimeout(() => {
                window.location.href = this.href;
            }, 500);
        });
    });
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
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert-dynamic');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dynamic`;
    alert.innerHTML = message;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'block';
    }
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) {
        loading.style.display = 'none';
    }
}

// Smooth scrolling for anchor links
function smoothScroll(target) {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Feature panel collapsible functionality
function initializeFeaturePanel() {
    const featureToggles = document.querySelectorAll('.feature-toggle');
    
    featureToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const content = this.nextElementSibling;
            const isExpanded = content.style.display !== 'none';
            
            content.style.display = isExpanded ? 'none' : 'block';
            this.textContent = isExpanded ? '▶' : '▼';
        });
    });
}

// Progressive enhancement for results page
if (window.location.pathname.includes('results')) {
    document.addEventListener('DOMContentLoaded', function() {
        initializeFeaturePanel();
        
        // Add copy functionality to feature values
        const featureValues = document.querySelectorAll('.feature-value');
        featureValues.forEach(value => {
            value.style.cursor = 'pointer';
            value.title = 'Click to copy';
            
            value.addEventListener('click', function() {
                navigator.clipboard.writeText(this.textContent).then(() => {
                    showAlert('Value copied to clipboard!', 'success');
                });
            });
        });
    });
}

// Error handling for image loading
document.addEventListener('DOMContentLoaded', function() {
    const spectrogramImages = document.querySelectorAll('.spectrogram-item img');
    
    spectrogramImages.forEach(img => {
        img.addEventListener('error', function() {
            this.style.display = 'none';
            const errorMsg = document.createElement('div');
            errorMsg.className = 'alert alert-danger';
            errorMsg.textContent = 'Error loading spectrogram image';
            this.parentNode.appendChild(errorMsg);
        });
    });
});

// Accessibility improvements
document.addEventListener('keydown', function(event) {
    // ESC key to close modals or clear forms
    if (event.key === 'Escape') {
        const fileInput = document.getElementById('file-input');
        if (fileInput && fileInput.value) {
            fileInput.value = '';
            const fileInfo = document.getElementById('file-info');
            if (fileInfo) {
                fileInfo.style.display = 'none';
            }
        }
    }
});

// Performance optimization: Lazy loading for images
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', initializeLazyLoading);
